import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CA_KEY_BITS = 4096
CA_DAYS = 3650
MIN_USER_KEY_BITS = 2048
USER_DAYS = 365
DEFAULT_STORE = Path(__file__).resolve().parent / "pki_data"


def find_openssl():
    found = shutil.which("openssl")
    if found:
        return found
    candidates = [
        Path(r"C:\Program Files\Git\usr\bin\openssl.exe"),
        Path(r"C:\Program Files\Git\mingw64\bin\openssl.exe"),
        Path(r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    raise FileNotFoundError("OpenSSL executable not found in PATH or standard Git/OpenSSL folders.")


OPENSSL_BIN = find_openssl()


def run_openssl(args, cwd=None, check=True):
    env = os.environ.copy()
    env["MSYS_NO_PATHCONV"] = "1"
    env["MSYS2_ARG_CONV_EXCL"] = "*"
    proc = subprocess.run(
        [OPENSSL_BIN] + [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"OpenSSL failed ({' '.join(str(a) for a in args)}): {msg}")
    return proc


def build_openssl_cnf(ca_dir):
    posix_dir = ca_dir.resolve().as_posix()
    return "\n".join([
        "[ ca ]",
        "default_ca = CA_default",
        "",
        "[ CA_default ]",
        f"dir               = {posix_dir}",
        "certs             = $dir/certs",
        "crl_dir           = $dir/crl",
        "new_certs_dir     = $dir/newcerts",
        "database          = $dir/index.txt",
        "serial            = $dir/serial",
        "crlnumber         = $dir/crlnumber",
        "RANDFILE          = $dir/private/.rand",
        "private_key       = $dir/private/ca.key.pem",
        "certificate       = $dir/certs/ca.cert.pem",
        "crl               = $dir/crl/ca.crl.pem",
        f"default_days      = {USER_DAYS}",
        "default_crl_days  = 30",
        "default_md        = sha256",
        "preserve          = no",
        "unique_subject    = no",
        "policy            = policy_loose",
        "crl_extensions    = crl_ext",
        "",
        "[ policy_loose ]",
        "countryName             = optional",
        "stateOrProvinceName     = optional",
        "localityName            = optional",
        "organizationName        = optional",
        "organizationalUnitName  = optional",
        "commonName              = supplied",
        "emailAddress            = optional",
        "",
        "[ req ]",
        "default_bits        = 2048",
        "distinguished_name  = req_distinguished_name",
        "string_mask         = utf8only",
        "default_md          = sha256",
        "x509_extensions     = v3_ca",
        "",
        "[ req_distinguished_name ]",
        "countryName                     = Country Name (2 letter code)",
        "stateOrProvinceName             = State or Province Name",
        "localityName                    = Locality Name",
        "organizationName                = Organization Name",
        "organizationalUnitName          = Organizational Unit Name",
        "commonName                      = Common Name",
        "emailAddress                    = Email Address",
        "",
        "[ v3_ca ]",
        "subjectKeyIdentifier = hash",
        "authorityKeyIdentifier = keyid:always,issuer",
        "basicConstraints = critical, CA:true",
        "keyUsage = critical, digitalSignature, cRLSign, keyCertSign",
        "",
        "[ usr_cert ]",
        "basicConstraints = CA:FALSE",
        "nsCertType = client, email",
        "nsComment = \"CS Lab 5 Internal PKI User Certificate\"",
        "subjectKeyIdentifier = hash",
        "authorityKeyIdentifier = keyid,issuer",
        "keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment",
        "extendedKeyUsage = clientAuth, emailProtection, codeSigning",
        "",
        "[ crl_ext ]",
        "authorityKeyIdentifier = keyid:always",
        "",
    ])


def ca_paths(base_dir):
    base = Path(base_dir).resolve()
    return {
        "base": base,
        "ca": base / "ca",
        "certs": base / "ca" / "certs",
        "crl": base / "ca" / "crl",
        "newcerts": base / "ca" / "newcerts",
        "private": base / "ca" / "private",
        "users": base / "users",
        "docs": base / "docs",
        "cnf": base / "ca" / "openssl.cnf",
        "index": base / "ca" / "index.txt",
        "serial": base / "ca" / "serial",
        "crlnumber": base / "ca" / "crlnumber",
        "ca_key": base / "ca" / "private" / "ca.key.pem",
        "ca_cert": base / "ca" / "certs" / "ca.cert.pem",
        "ca_crl": base / "ca" / "crl" / "ca.crl.pem",
        "ca_bundle": base / "ca" / "crl" / "ca_chain_crl.pem",
    }


def user_paths(base_dir, username):
    clean = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in username.strip())
    if not clean:
        raise ValueError("Username cannot be empty.")
    udir = Path(base_dir).resolve() / "users" / clean
    return {
        "name": clean,
        "dir": udir,
        "key": udir / f"{clean}.key.pem",
        "csr": udir / f"{clean}.csr.pem",
        "cert": udir / f"{clean}.cert.pem",
        "pub": udir / f"{clean}.pub.pem",
    }


def rebuild_crl(base_dir):
    p = ca_paths(base_dir)
    run_openssl(["ca", "-batch", "-config", p["cnf"], "-gencrl", "-out", p["ca_crl"]])
    bundle_text = p["ca_cert"].read_text(encoding="utf-8") + "\n" + p["ca_crl"].read_text(encoding="utf-8")
    p["ca_bundle"].write_text(bundle_text, encoding="utf-8")
    return p["ca_crl"]


def init_ca(base_dir, cn="UTM FAF-242 Internal Root CA", reset=False):
    p = ca_paths(base_dir)
    if reset and p["base"].exists():
        shutil.rmtree(p["base"])
    for key in ("ca", "certs", "crl", "newcerts", "private", "users", "docs"):
        p[key].mkdir(parents=True, exist_ok=True)
    if not p["index"].exists():
        p["index"].write_text("", encoding="utf-8")
    if not p["serial"].exists():
        p["serial"].write_text("1000\n", encoding="utf-8")
    if not p["crlnumber"].exists():
        p["crlnumber"].write_text("1000\n", encoding="utf-8")
    p["cnf"].write_text(build_openssl_cnf(p["ca"]), encoding="utf-8")

    run_openssl(["genrsa", "-out", p["ca_key"], str(CA_KEY_BITS)])
    subj = f"/C=MD/ST=Chisinau/L=Chisinau/O=UTM FCIM/OU=FAF-242 Cryptography/CN={cn}"
    run_openssl([
        "req", "-config", p["cnf"],
        "-key", p["ca_key"],
        "-new", "-x509",
        "-days", str(CA_DAYS),
        "-sha256",
        "-extensions", "v3_ca",
        "-out", p["ca_cert"],
        "-subj", subj,
    ])
    rebuild_crl(base_dir)
    return p


def ensure_ca(base_dir):
    p = ca_paths(base_dir)
    if not (p["ca_key"].exists() and p["ca_cert"].exists() and p["cnf"].exists()):
        raise RuntimeError("CA is not initialized yet. Run option 1 (Initialize CA) first.")
    return p


def issue_user(base_dir, username, bits=MIN_USER_KEY_BITS, email=None):
    p = ensure_ca(base_dir)
    if bits < MIN_USER_KEY_BITS:
        raise ValueError(f"User RSA key must be at least {MIN_USER_KEY_BITS} bits (got {bits}).")
    u = user_paths(base_dir, username)
    u["dir"].mkdir(parents=True, exist_ok=True)

    run_openssl(["genrsa", "-out", u["key"], str(bits)])
    mail = email or f"{u['name']}@faf242.utm.md"
    subj = f"/C=MD/ST=Chisinau/L=Chisinau/O=UTM FCIM/OU=FAF-242/CN={u['name']}/emailAddress={mail}"
    run_openssl([
        "req", "-config", p["cnf"],
        "-key", u["key"],
        "-new", "-sha256",
        "-out", u["csr"],
        "-subj", subj,
    ])
    run_openssl([
        "ca", "-batch", "-config", p["cnf"],
        "-extensions", "usr_cert",
        "-days", str(USER_DAYS),
        "-notext", "-md", "sha256",
        "-in", u["csr"],
        "-out", u["cert"],
    ])
    pub_proc = run_openssl(["x509", "-in", u["cert"], "-pubkey", "-noout"])
    u["pub"].write_text(pub_proc.stdout, encoding="utf-8")
    return u


def check_cert_trust(base_dir, cert_path):
    p = ensure_ca(base_dir)
    if not p["ca_bundle"].exists():
        rebuild_crl(base_dir)
    proc = run_openssl(["verify", "-crl_check", "-CAfile", p["ca_bundle"], cert_path], check=False)
    combined = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode == 0, combined


def revoke_user(base_dir, username, reason="keyCompromise"):
    p = ensure_ca(base_dir)
    u = user_paths(base_dir, username)
    if not u["cert"].exists():
        raise FileNotFoundError(f"Certificate not found for user '{username}'.")
    run_openssl(["ca", "-batch", "-config", p["cnf"], "-revoke", u["cert"], "-crl_reason", reason])
    crl_path = rebuild_crl(base_dir)
    return crl_path


def sign_file(base_dir, username, file_path, sig_path=None):
    ensure_ca(base_dir)
    u = user_paths(base_dir, username)
    if not u["key"].exists() or not u["cert"].exists():
        raise FileNotFoundError(f"User '{username}' does not have an issued key/certificate.")
    trusted, trust_msg = check_cert_trust(base_dir, u["cert"])
    if not trusted:
        raise RuntimeError(f"Signing refused: certificate for '{u['name']}' is not valid/trusted.\n{trust_msg}")
    target = Path(file_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Input file not found: {target}")
    out_sig = Path(sig_path).resolve() if sig_path else Path(str(target) + f".{u['name']}.sig")
    run_openssl(["dgst", "-sha256", "-sign", u["key"], "-out", out_sig, target])
    return out_sig


def verify_file(base_dir, username, file_path, sig_path):
    ensure_ca(base_dir)
    u = user_paths(base_dir, username)
    if not u["cert"].exists():
        raise FileNotFoundError(f"Certificate not found for user '{username}'.")
    target = Path(file_path).resolve()
    sig = Path(sig_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Input file not found: {target}")
    if not sig.exists():
        raise FileNotFoundError(f"Signature file not found: {sig}")

    trusted, trust_msg = check_cert_trust(base_dir, u["cert"])
    pub_proc = run_openssl(["x509", "-in", u["cert"], "-pubkey", "-noout"])
    u["pub"].write_text(pub_proc.stdout, encoding="utf-8")
    sig_proc = run_openssl(["dgst", "-sha256", "-verify", u["pub"], "-signature", sig, target], check=False)
    sig_msg = (sig_proc.stdout + "\n" + sig_proc.stderr).strip()
    sig_ok = sig_proc.returncode == 0 and "Verified OK" in sig_msg
    return {
        "trusted": trusted,
        "trust_msg": trust_msg,
        "sig_ok": sig_ok,
        "sig_msg": sig_msg,
        "overall_ok": trusted and sig_ok,
    }


def cert_summary(cert_path):
    proc = run_openssl(["x509", "-in", cert_path, "-noout", "-subject", "-issuer", "-serial", "-dates", "-text"])
    lines = proc.stdout.splitlines()
    keep = []
    for line in lines:
        s = line.strip()
        if any(s.startswith(prefix) for prefix in (
            "subject=", "issuer=", "serial=", "notBefore=", "notAfter=",
            "Public Key Algorithm:", "Public-Key:", "Signature Algorithm:",
        )) and s not in keep:
            keep.append(s)
    return "\n".join(keep)


def print_ca_status(base_dir):
    p = ensure_ca(base_dir)
    print("=== ROOT CA CERTIFICATE ===")
    print(cert_summary(p["ca_cert"]))
    print("\n=== CA DATABASE (index.txt) ===")
    idx_txt = p["index"].read_text(encoding="utf-8").strip()
    print(idx_txt if idx_txt else "(empty)")
    print("\n=== REVOKED CERTIFICATES IN CRL ===")
    crl_out = run_openssl(["crl", "-in", p["ca_crl"], "-noout", "-text"]).stdout
    for line in crl_out.splitlines():
        if any(k in line for k in ("Issuer:", "Last Update:", "Next Update:", "Serial Number:", "Revocation Date:", "CRL Reason", "No Revoked Certificates")):
            print(line)


def run_demo_and_tests(work_dir=None, keep=False):
    own_tmp = work_dir is None
    target_dir = Path(tempfile.mkdtemp(prefix="cs_lab5_pki_")) if own_tmp else Path(work_dir).resolve()
    try:
        print("=" * 74)
        print("CRYPTOGRAPHY LAB 5 - INTERNAL PKI & DIGITAL SIGNATURES (OPENSSL)")
        print(f"OpenSSL Binary : {OPENSSL_BIN}")
        ver = run_openssl(["version"]).stdout.strip()
        print(f"OpenSSL Version: {ver}")
        print(f"Store Directory: {target_dir}")
        print("=" * 74)

        print("\n[1] Initializing Internal Root CA (RSA 4096-bit, validity 3650 days)...")
        p = init_ca(target_dir, cn="UTM FAF-242 Root CA", reset=True)
        ca_info = cert_summary(p["ca_cert"])
        print(ca_info)
        assert "Public-Key: (4096 bit)" in ca_info

        print("\n[2] Issuing user RSA keys (2048-bit, validity 365 days)...")
        weak_rejected = False
        try:
            issue_user(target_dir, "weak_test", bits=1024)
        except ValueError:
            weak_rejected = True
            print("[PASS] Rejected 1024-bit user key (minimum 2048 bits enforced).")
        assert weak_rejected
        u_ion = issue_user(target_dir, "ion_morosanu", bits=2048, email="ion.morosanu@isa.utm.md")
        ion_info = cert_summary(u_ion["cert"])
        print("--- User: ion_morosanu ---")
        print(ion_info)
        assert "Public-Key: (2048 bit)" in ion_info

        u_alice = issue_user(target_dir, "alice_popescu", bits=2048, email="alice.popescu@isa.utm.md")
        alice_info = cert_summary(u_alice["cert"])
        print("--- User: alice_popescu ---")
        print(alice_info)
        assert "Public-Key: (2048 bit)" in alice_info

        ok_ion, msg_ion = check_cert_trust(target_dir, u_ion["cert"])
        print(f"Trust check (ion_morosanu): {ok_ion} -> {msg_ion}")
        assert ok_ion

        doc_path = p["docs"] / "contract_faf242.txt"
        doc_path.write_text(
            "Technical University of Moldova - FAF-242\n"
            "Authorized transaction document for CS Lab 5 PKI & Digital Signatures.\n",
            encoding="utf-8",
        )
        print(f"\n[3] Signing document '{doc_path.name}' as 'ion_morosanu'...")
        sig_path = sign_file(target_dir, "ion_morosanu", doc_path)
        sig_bytes = sig_path.read_bytes()
        print(f"Signature created: {sig_path.name} ({len(sig_bytes)} bytes / {len(sig_bytes) * 8} bits)")
        print(f"Signature preview (hex): {sig_bytes[:24].hex().upper()}...")

        print("\n[4] Verifying original document with ion_morosanu's certificate...")
        v1 = verify_file(target_dir, "ion_morosanu", doc_path, sig_path)
        print(f"Trust: {v1['trusted']} ({v1['trust_msg']})")
        print(f"Signature: {v1['sig_ok']} ({v1['sig_msg']})")
        print(f"Overall Verdict: {'VALID' if v1['overall_ok'] else 'INVALID'}")
        assert v1["overall_ok"]

        tampered = p["docs"] / "contract_tampered.txt"
        tampered.write_text(
            "Technical University of Moldova - FAF-242\n"
            "Modified transaction document (amount altered!).\n",
            encoding="utf-8",
        )
        print(f"\n[5] Verifying tampered document '{tampered.name}' against original signature...")
        v2 = verify_file(target_dir, "ion_morosanu", tampered, sig_path)
        print(f"Signature: {v2['sig_ok']} ({v2['sig_msg']})")
        print(f"Overall Verdict: {'VALID' if v2['overall_ok'] else 'INVALID'}")
        assert not v2["sig_ok"] and not v2["overall_ok"]

        print("\n[6] Verifying ion_morosanu's signature with alice_popescu's certificate (wrong signer)...")
        v3 = verify_file(target_dir, "alice_popescu", doc_path, sig_path)
        print(f"Signature: {v3['sig_ok']} ({v3['sig_msg']})")
        print(f"Overall Verdict: {'VALID' if v3['overall_ok'] else 'INVALID'}")
        assert not v3["sig_ok"] and not v3["overall_ok"]

        print("\n[7] Revoking ion_morosanu's certificate (reason: keyCompromise) & updating CRL...")
        revoke_user(target_dir, "ion_morosanu", reason="keyCompromise")
        v4 = verify_file(target_dir, "ion_morosanu", doc_path, sig_path)
        print(f"Trust after revocation: {v4['trusted']} -> {v4['trust_msg']}")
        print(f"Cryptographic signature: {v4['sig_ok']} ({v4['sig_msg']})")
        print(f"Overall PKI Verdict: {'VALID' if v4['overall_ok'] else 'REJECTED (CERT REVOKED)'}")
        assert not v4["trusted"] and not v4["overall_ok"] and "revoked" in v4["trust_msg"].lower()

        print("\n[8] Attempting to sign a new file with revoked user key...")
        refused = False
        try:
            sign_file(target_dir, "ion_morosanu", doc_path)
        except RuntimeError as exc:
            refused = True
            print(f"[PASS] Signing blocked as expected: {str(exc).splitlines()[0]}")
        assert refused

        print("\n[9] Re-issuing fresh 2048-bit key & certificate for ion_morosanu and signing again...")
        u_reissued = issue_user(target_dir, "ion_morosanu", bits=2048, email="ion.morosanu@isa.utm.md")
        sig2_path = sign_file(target_dir, "ion_morosanu", doc_path)
        v5 = verify_file(target_dir, "ion_morosanu", doc_path, sig2_path)
        print(cert_summary(u_reissued["cert"]))
        print(f"New cert & signature verdict: {'VALID' if v5['overall_ok'] else 'INVALID'}")
        assert v5["overall_ok"]

        print("\n[10] Final CA state:")
        print_ca_status(target_dir)
        print("\n[PASS] All PKI & Digital Signature tests passed.")
    finally:
        if own_tmp and not keep:
            shutil.rmtree(target_dir, ignore_errors=True)


def interactive_cli(base_dir=DEFAULT_STORE):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 74)
    print("   Internal PKI & Digital Signatures (OpenSSL) - CS Lab 5")
    print("   Student: Ion Moroșanu, FAF-242 | TUM 2026")
    print(f"   CA: RSA {CA_KEY_BITS}-bit ({CA_DAYS} days) | User: RSA >={MIN_USER_KEY_BITS}-bit ({USER_DAYS} days)")
    print("=" * 74)

    while True:
        print("\nChoose an option:")
        print("  1. Initialize Internal Root CA (RSA 4096-bit, 3650 days)")
        print("  2. Issue User RSA Key & Certificate (>=2048-bit, 365 days)")
        print("  3. Sign a Document / File")
        print("  4. Verify a Signature + PKI Certificate Chain (with CRL check)")
        print("  5. Revoke User Certificate & Update CRL")
        print("  6. Show CA Status, Issued Certificates & CRL")
        print("  7. Run Full Automated PKI + Signature Demo")
        print("  0. Exit")

        choice = input("\nEnter choice (0-7): ").strip()
        try:
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                cn = input("CA Common Name [UTM FAF-242 Root CA]: ").strip() or "UTM FAF-242 Root CA"
                p = init_ca(base_dir, cn=cn, reset=True)
                print(f"\n[+] Root CA initialized in {p['ca']}")
                print(cert_summary(p["ca_cert"]))
            elif choice == "2":
                username = input("Username (e.g. ion_morosanu): ").strip()
                bits_raw = input("Key size in bits [2048]: ").strip() or "2048"
                email = input("Email (optional): ").strip() or None
                u = issue_user(base_dir, username, bits=int(bits_raw), email=email)
                print(f"\n[+] Certificate issued for '{u['name']}':")
                print(cert_summary(u["cert"]))
            elif choice == "3":
                username = input("Signer username: ").strip()
                fpath = input("Path to file to sign: ").strip().strip('"')
                sig = sign_file(base_dir, username, fpath)
                print(f"\n[+] Signed successfully -> {sig}")
            elif choice == "4":
                username = input("Signer username: ").strip()
                fpath = input("Path to file: ").strip().strip('"')
                spath = input("Path to signature file: ").strip().strip('"')
                res = verify_file(base_dir, username, fpath, spath)
                print(f"\nCertificate Trust (CA + CRL): {res['trusted']} -> {res['trust_msg']}")
                print(f"Signature Check (SHA-256 RSA): {res['sig_ok']} -> {res['sig_msg']}")
                print(f"Overall Result: {'VALID' if res['overall_ok'] else 'INVALID'}")
            elif choice == "5":
                username = input("Username to revoke: ").strip()
                reason = input("Reason [keyCompromise]: ").strip() or "keyCompromise"
                crl = revoke_user(base_dir, username, reason=reason)
                print(f"\n[+] Revoked '{username}' and updated CRL at {crl}")
            elif choice == "6":
                print_ca_status(base_dir)
            elif choice == "7":
                run_demo_and_tests()
            else:
                print("Invalid option. Choose 0-7.")
        except Exception as exc:
            print(f"[-] Error: {exc}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_demo_and_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        out_dir = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_STORE)
        run_demo_and_tests(work_dir=out_dir, keep=True)
    else:
        try:
            interactive_cli()
        except (EOFError, KeyboardInterrupt):
            print("\nTerminated.")

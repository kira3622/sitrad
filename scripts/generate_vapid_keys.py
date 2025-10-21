 7V120.¤import base64
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except Exception as e:
    raise SystemExit("cryptography package is required. Install with: pip install cryptography")

# Generate EC P-256 private key
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

# Serialize private key to PEM (PKCS8)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Compute uncompressed public key (0x04 + X(32) + Y(32))
public_key = private_key.public_key()
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Base64url (without padding) of uncompressed public key
vapid_public_key = base64.urlsafe_b64encode(public_bytes).decode('ascii').rstrip('=')

# Write private key PEM to project root
out_path = Path(__file__).resolve().parent.parent / 'vapid_private.pem'
out_path.write_bytes(private_pem)

print("VAPID_PRIVATE_PEM_FILE:", str(out_path))
print("VAPID_PUBLIC_KEY:", vapid_public_key)
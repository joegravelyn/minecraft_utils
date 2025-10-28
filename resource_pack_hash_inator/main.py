from pathlib import Path
import hashlib

def main():
   rp_zip = Path(input("Resource Pack Zip File: "))

   sha1 = hashlib.sha1()
   with rp_zip.open("rb") as file:
      while chunk := file.read(8192):
         sha1.update(chunk)
   print(sha1.hexdigest())


if __name__ == "__main__":
   main()
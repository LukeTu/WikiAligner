"""Entry point for the PyInstaller bundle (the package's __main__ uses relative imports)."""
import multiprocessing

from wikialigner.desktop import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

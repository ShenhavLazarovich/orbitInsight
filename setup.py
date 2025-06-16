from setuptools import setup, find_packages

setup(
    name="orbit-insight",
    version="0.1.0",
    packages=find_packages(where=".", exclude=["static*", "attached_assets*"]),
    python_requires=">=3.11",
    install_requires=[
        "numpy>=2.2.5",
        "openai>=1.77.0",
        "pandas>=2.2.3",
        "plotly>=6.0.1",
        "requests>=2.32.3",
        "scipy>=1.15.2",
        "sgp4>=2.24",
        "streamlit>=1.45.0",
    ],
) 
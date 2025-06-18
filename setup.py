from setuptools import setup, find_packages

setup(
    name="echo-kernel",
    version="0.1.0",
    description="A flexible and extensible Python framework for building AI-powered applications",
    author="Ronmenator",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "numpy>=1.21.0",
        "qdrant-client>=1.7.0",
        "faiss-cpu>=1.7.0",
        "python-dotenv>=1.0.0",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    python_requires=">=3.8",
) 
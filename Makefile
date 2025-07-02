add-install-files:
	git add uv.lock requirements/ pyproject.toml

install:
	uv add -r requirements/requirements.txt

dev-install:
	uv add -r requirements/dev.requirements.txt

clean-runs:
	rm -rf experiments/ch07/runs/*
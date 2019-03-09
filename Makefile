all:
	python3 -b src/main.py

clean:
	rm -rf logs.txt *.db *.json *.db-journal

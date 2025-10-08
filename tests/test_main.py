import csv
import sys
from main import read_csv_files, parse_args, main


def test_read_csv_files(tmp_path):
    csv_file = tmp_path / "test.csv"
    with csv_file.open("w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "brand", "price", "rating"])
        writer.writerow(["test product", "apple", "100", "4.5"])

    rows = read_csv_files([str(csv_file)])
    assert len(rows) == 1
    assert rows[0]["brand"] == "apple"


def test_parse_args(monkeypatch):
    test_args = ["main.py", "--files", "file1.csv", "file2.csv", "--report", "average-rating"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_args()
    assert args.files == ["file1.csv", "file2.csv"]
    assert args.report == "average-rating"


def test_main_output(monkeypatch, tmp_path, capsys):
    csv_file = tmp_path / "test.csv"
    with csv_file.open("w", newline='', encoding="utf-8") as f:
        f.write("name,brand,price,rating\n")
        f.write("p1,apple,100,5.0\n")
        f.write("p2,samsung,200,4.0\n")

    test_args = ["main.py", "--files", str(csv_file), "--report", "average-rating"]
    monkeypatch.setattr(sys, "argv", test_args)
    main()
    # capsys to get result out of console
    captured = capsys.readouterr()
    assert "apple" in captured.out
    assert "samsung" in captured.out
    assert "Average Rating" in captured.out
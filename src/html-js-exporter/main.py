from exporters.html_exporter import HTMLExporter


def main():
    exporter = HTMLExporter()
    exporter.export(
        ir_path="data/AirFryer_Philips_HD9252.json",
        output_path="output/wizard.html"
    )


if __name__ == "__main__":
    main()
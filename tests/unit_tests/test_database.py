import sonar.database


def test_find_fpga_family():
    fpgas = [
        ("xcku3p-ffva676-1L-i", "Kintex_Ultrascale_Plus"),
        ("xcku115-flva1517-2-e", "Kintex_Ultrascale"),
        ("xcvu3p-ffvc1517-2L-e", "Virtex_Ultrascale_Plus"),
        ("xcvu065-ffvc1517-2-e", "Virtex_Ultrascale"),
        ("xc7v2000tflg1925-1", "7series_Virtex"),
        ("zc7z007sclg400-1", "7series_Zynq"),
        ("xc7k70tfbg676-3", "7series_Kintex"),
        ("xczu2cg-sbva484-2-e", "Zynq_Ultrascale_Plus"),
    ]

    for fpga in fpgas:
        family = sonar.database.Database.Board._find_part_family(fpga[0])
        assert family == fpga[1]

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


RISK_COLORS = {
    "HIGH": "#F87171",
    "MEDIUM": "#FBBF24",
    "LOW": "#34D399",
}


AUTHENTIC_STATUSES = {
    "AUTHENTIC",
    "REAL",
    "GENUINE",
}


def _safe(
    value,
    default="Not available",
):
    if value is None or value == "":
        return default

    return str(value)


def _get_modality(
    result: dict,
) -> str:

    if (
        "suspicious_segments"
        in result
        or "frame_scores"
        in result
    ):
        return "Video"

    if "suspicious_ranges" in result:
        return "Audio"

    return "Image"


def _confidence_percentage(
    value,
) -> float:

    try:
        value = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    # Assessment confidence is always stored internally
    # as a 0–1 fraction.

    value = max(
        0.0,
        min(
            1.0,
            value,
        ),
    )

    return value * 100


def generate_report(
    result: dict,
) -> BytesIO:

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
    )

    styles = getSampleStyleSheet()

    # --------------------------------------------------
    # STYLES
    # --------------------------------------------------

    title_style = ParagraphStyle(
        "DeepTraceTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=colors.HexColor(
            "#0B1220"
        ),
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor(
            "#64748B"
        ),
        alignment=TA_CENTER,
        spaceAfter=24,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor(
            "#0F766E"
        ),
        spaceBefore=18,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor(
            "#334155"
        ),
    )

    small_style = ParagraphStyle(
        "Small",
        parent=normal_style,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(
            "#64748B"
        ),
    )

    verdict_style = ParagraphStyle(
        "Verdict",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#0F172A"
        ),
    )

    story = []

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    modality = _get_modality(
        result
    )

    story.append(
        Paragraph(
            "DEEPTRACE",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Digital Media Forensics Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Analysis Type: {modality}",
            subtitle_style,
        )
    )

    # --------------------------------------------------
    # ASSESSMENT
    # --------------------------------------------------

    assessment = result.get(
        "assessment",
        {},
    )

    classification = _safe(
        assessment.get(
            "classification"
        )
    ).upper()

    confidence = _confidence_percentage(
        assessment.get(
            "confidence",
            0,
        )
    )

    trust_score = int(
        assessment.get(
            "trust_score",
            0,
        )
    )

    risk_level = _safe(
        assessment.get(
            "risk_level",
            "LOW",
        )
    ).upper()

    risk_color = RISK_COLORS.get(
        risk_level,
        "#64748B",
    )

    story.append(
        Paragraph(
            "Overall Assessment",
            section_style,
        )
    )

    story.append(
        Paragraph(
            classification,
            verdict_style,
        )
    )

    story.append(
        Spacer(
            1,
            12,
        )
    )

    assessment_data = [
        [
            "Risk Level",
            risk_level,
        ],
        [
            "Authenticity Confidence",
            f"{confidence:.0f}%",
        ],
        [
            "Trust Score",
            f"{trust_score}/100",
        ],
        [
            "Media Type",
            modality,
        ],
    ]

    assessment_table = Table(
        assessment_data,
        colWidths=[
            2.2 * inch,
            3.5 * inch,
        ],
    )

    assessment_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#E2E8F0"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    colors.HexColor(
                        risk_color
                    ),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CBD5E1"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        assessment_table
    )

    # --------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------

    file_info = result.get(
        "file_info",
        {},
    )

    if file_info:

        story.append(
            Paragraph(
                "File Information",
                section_style,
            )
        )

        file_data = []

        for key, value in (
            file_info.items()
        ):

            formatted_key = (
                key.replace(
                    "_",
                    " ",
                ).title()
            )

            file_data.append(
                [
                    formatted_key,
                    _safe(value),
                ]
            )

        file_table = Table(
            file_data,
            colWidths=[
                2.2 * inch,
                3.5 * inch,
            ],
        )

        file_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor(
                            "#F1F5F9"
                        ),
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#CBD5E1"
                        ),
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                ]
            )
        )

        story.append(
            file_table
        )

    # --------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------

    evidence = result.get(
        "evidence",
        [],
    )

    story.append(
        Paragraph(
            "Evidence Summary",
            section_style,
        )
    )

    if evidence:

        evidence_data = [
            [
                "Source",
                "Score",
                "Finding",
            ]
        ]

        for item in evidence:

            try:

                score = (
                    float(
                        item.get(
                            "score",
                            0,
                        )
                    )
                    * 100
                )

            except (
                TypeError,
                ValueError,
            ):

                score = 0

            evidence_data.append(
                [
                    _safe(
                        item.get(
                            "source"
                        )
                    ),
                    f"{score:.0f}%",
                    _safe(
                        item.get(
                            "explanation"
                        )
                    ),
                ]
            )

        evidence_table = Table(
            evidence_data,
            colWidths=[
                1.4 * inch,
                0.8 * inch,
                3.5 * inch,
            ],
            repeatRows=1,
        )

        evidence_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#0F766E"
                        ),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(
                            "#CBD5E1"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            evidence_table
        )

    else:

        story.append(
            Paragraph(
                "No evidence signals were returned.",
                normal_style,
            )
        )

    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------

    metadata = result.get(
        "metadata",
        {},
    )

    findings = metadata.get(
        "findings",
        [],
    )

    if metadata:

        story.append(
            Paragraph(
                "Metadata Findings",
                section_style,
            )
        )

        if findings:

            for finding in findings:

                story.append(
                    Paragraph(
                        f"• {_safe(finding)}",
                        normal_style,
                    )
                )

                story.append(
                    Spacer(
                        1,
                        5,
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No metadata irregularities were detected.",
                    normal_style,
                )
            )

    # --------------------------------------------------
    # VIDEO SEGMENTS
    # --------------------------------------------------

    suspicious_segments = result.get(
        "suspicious_segments",
        [],
    )

    if suspicious_segments:

        story.append(
            Paragraph(
                "Suspicious Video Segments",
                section_style,
            )
        )

        segment_data = [
            [
                "Start",
                "End",
                "Severity",
            ]
        ]

        for segment in (
            suspicious_segments
        ):

            segment_data.append(
                [
                    f"{segment.get('start_pct', 0)}%",
                    f"{segment.get('end_pct', 0)}%",
                    _safe(
                        segment.get(
                            "severity"
                        )
                    ),
                ]
            )

        segment_table = Table(
            segment_data,
            colWidths=[
                2 * inch,
                2 * inch,
                2 * inch,
            ],
        )

        segment_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#7C3AED"
                        ),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#CBD5E1"
                        ),
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            segment_table
        )

    # --------------------------------------------------
    # AUDIO RANGES
    # --------------------------------------------------

    suspicious_ranges = result.get(
        "suspicious_ranges",
        [],
    )

    if suspicious_ranges:

        story.append(
            Paragraph(
                "Flagged Audio Regions",
                section_style,
            )
        )

        audio_data = [
            [
                "Start",
                "End",
            ]
        ]

        for start, end in (
            suspicious_ranges
        ):

            audio_data.append(
                [
                    str(start),
                    str(end),
                ]
            )

        audio_table = Table(
            audio_data,
            colWidths=[
                3 * inch,
                3 * inch,
            ],
        )

        audio_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#B91C1C"
                        ),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#CBD5E1"
                        ),
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            audio_table
        )

    # --------------------------------------------------
    # REPORT INFORMATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Report Information",
            section_style,
        )
    )

    generated_at = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"Generated: {generated_at}",
            normal_style,
        )
    )

    story.append(
        Spacer(
            1,
            12,
        )
    )

    story.append(
        Paragraph(
            "Disclaimer: This report represents an automated "
            "forensic assessment based on the available detection "
            "models and evidence signals. Results should be "
            "interpreted as decision-support information and "
            "not as definitive proof of authenticity or manipulation.",
            small_style,
        )
    )

    # --------------------------------------------------
    # BUILD
    # --------------------------------------------------

    doc.build(
        story
    )

    buffer.seek(0)

    return buffer
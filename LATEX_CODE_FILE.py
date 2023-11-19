LATEX_CODE = """
\\documentclass{article}
\\usepackage{bubblecv}

\\begin{document}


\\begin{cv}[avatar]{James Bond}{Secret Agent}


\\cvsection[summary]{Profile}  %-----------------------------------------------------------

Highly skilled secret agent with a license to kill. 
Bringing together outstanding combat and intelligence abilities with a charismatic and persuasive personality. 
A dedicated and adaptable professional committed to global security.


\\cvsection[work]{Work experience}  %------------------------------------------------------

\\begin{cvevent}[1962][present]
    \\cvname{Secret Agent}
    \\cvdescription{MI6 Intelligence Agency, London}
    \\begin{itemize}
        \\item Covert intelligence operations for national security.
        \\item Infiltration from high-risk environments.
        \\item Utilization of advanced espionage techniques and gadgets.
        \\item Surveillance, analysis, and threat prevention.
    \\end{itemize}
\\end{cvevent}


\\cvsection[education]{Education}  %------------------------------------------------------

\\begin{cvevent}[1958][1962]
    \\cvname{Intelligence Academy}
    \\cvdescription{MI6 Training Facility, London}
    \\textbf{Courses and Achievements:}
    \\begin{itemize}
        \\item Mastered advanced techniques for discreetly gathering intelligence and conducting covert operations.
        \\item Trained extensively in planning and executing covert operations and infiltrating high-security areas.
        \\item Received rigorous combat training in martial arts, firearms handling, and tactical skills.
        \\item Proficient in surveillance methods, counter-surveillance techniques, and analyzing gathered intelligence.
    \\end{itemize}
\\end{cvevent}


\\cvsection[target]{Missions}  %----------------------------------------------------------

\\begin{cvevent}[2002]
    \\cvname{Die Another Day}
    Uncovered a North Korean general's plan to use a satellite weapon to create a war between North and South Korea.
\\end{cvevent}

\\cvseparator[2]
\\begin{cvevent}[1999]
    \\cvname{The World Is Not Enough}
    Protected an oil heiress from a terrorist plotting to exploit her family's resources and trigger a global meltdown.
\\end{cvevent}

\\cvseparator[2]
\\begin{cvevent}[1997]
    \\cvname{Tomorrow Never Dies}
    Investigated a media mogul's plot to provoke a war between the UK and China for increased ratings and power.
\\end{cvevent}

\\cvseparator[2]
\\begin{cvevent}[1995]
    \\cvname{GoldenEye}
    Prevented the use of the GoldenEye satellite weapon system by a rogue agent to cause global financial chaos.
\\end{cvevent}


\\cvsidebar %-----------------------------------------------------------------------------


\\cvsection[contact]{Contact}  %----------------------------------------------------------

\\begin{cvitem}[Envelope][4]
    \\textbf{Email}\\
    \\href{mailto:james.bond@mi6.gov}{\\texttt{james.bond@mi6.gov}}
\\end{cvitem}

\\cvseparator[3]
\\begin{cvitem}[Phone][4]
    \\textbf{Phone}\\
    \\href{tel:+442071234567}{\\texttt{+44 207 123 4567}}
\\end{cvitem}

\\cvseparator[3]
\\begin{cvitem}[Home][4]
    \\textbf{Address}\\
    MI6 Headquarters\\ London, United Kingdom
\\end{cvitem}

\\cvseparator[3]
\\begin{cvitem}[Globe][4]
    \\textbf{Website}\\
    \\href{https://www.mi6.gov.uk}{\\texttt{www.mi6.gov.uk}}
\\end{cvitem}


\\cvsection[skills]{Skills}  %-----------------------------------------------------------

\\begin{cvitem}
    Espionage Techniques
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Surveillance
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Combat Training
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Infiltration
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Problem Solving
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Effective Communication
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Adaptability
\\end{cvitem}

\\cvseparator
\\begin{cvitem}
    Teamwork
\\end{cvitem}


\\cvsection[languages]{Languages}  %--------------------------------------------------------

\\cvskill{English}{Fluent}{1.0}
\\cvskill{French}{Intermediate}{0.6}
\\cvskill{Russian}{Basic}{0.3}


\\end{cv}

\\cvfootnote{
    \\tiny I agree to the processing of personal data provided in this document for realizing the recruitment process pursuant to the Personal Data Protection Act of 10 May 2018 (Journal of Laws 2018, item 1000) and in agreement with Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation)
}

\\end{document}

"""
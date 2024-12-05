<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:atom="http://www.w3.org/2005/Atom">
	<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<meta name="referrer" content="unsafe-url" />
		<title><xsl:value-of select="/atom:feed/atom:title"/></title>
		<link rel="stylesheet" href="/layouts/water.min.css" />
	</head>
	<body>
		<h1>
			<img alt="feed icon" src="/images/profile.png" style="height:1em;vertical-align:middle;" />&#xa0;
			<img alt="feed icon 2" src="/atom:feed/atom:logo" style="height:1em;vertical-align:middle;" />&#xa0;
			<xsl:value-of select="/atom:feed/atom:title"/>
		</h1>

		<p>
			<xsl:value-of select="/atom:feed/atom:subtitle"/>
		</p>

		<a class="head_link">
              <xsl:attribute name="href">
				<xsl:value-of select="/atom:feed/atom:link[@rel='alternate']/@href | /atom:feed/atom:link[not(@rel)]/@href"/>
              </xsl:attribute>
              Visit Website &#x2192;
            </a>

		<p>
			This is the Atom&#xa0;<a href="https://www.rss.style/what-is-a-feed.html">news feed</a>&#xa0;for the&#xa0;
			<a><xsl:attribute name="href">
				<xsl:value-of select="/atom:feed/atom:link[@rel='alternate']/@href | /atom:feed/atom:link[not(@rel)]/@href"/>
			</xsl:attribute>
			<xsl:value-of select="/atom:feed/atom:title"/></a>&#xa0;
			website.
		</p>

		<p>It is meant for&#xa0;<a href="https://www.rss.style/newsreaders.html">news readers</a>, not humans.  Please copy-and-paste the URL into your news reader!</p>

		<p>
			<pre>
				<code id="feedurl"><xsl:value-of select="/atom:feed/atom:link[@rel='self']/@href"/></code>
			</pre>
		</p>
		
		<p><xsl:value-of select="count(/atom:feed/atom:entry)"/> news items.</p>

		<xsl:for-each select="/atom:feed/atom:entry">
			<details><summary>
				<a>
				<xsl:attribute name="href">
					<xsl:value-of select="atom:id"/>
				</xsl:attribute>
				<xsl:value-of select="atom:title"/>
				</a>&#xa0;-&#xa0;
				<!-- <xsl:value-of select="atom:updated" /> -->
				<!-- <xsl:value-of select="format-date(atom:published,'[D01].[M01].[Y0001]')" /> -->
				<!-- <xsl:value-of select="atom:published" /> -->
				<!-- <xsl:call-template name="format-date-string">
					<xsl:with-param name="date" select="atom:published"/>
					<xsl:with-param name="mask">mmm ddd d</xsl:with-param>
				</xsl:call-template> -->
				<xsl:call-template name="format-date">
				    <xsl:with-param name="date" select="atom:published"/>
				</xsl:call-template>
				</summary>
				<xsl:choose>
					<xsl:when test="atom:content">
						<xsl:value-of disable-output-escaping="yes" select="atom:content" />
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="atom:summary" />
					</xsl:otherwise>
				</xsl:choose>
				</details>
		</xsl:for-each>
		<p>Unless stated otherwise, all content on this feed is published under CC-BY-SA. All code on this site is available under the MPL.</p>
	</body>
</html>
	</xsl:template>

	<xsl:template name="format-date">
		<xsl:param name="date"/>
		<!-- 2024-12-04T22:17:41.207038+00:00 -->
		<!-- <xsl:variable name="date" select="'2024-12-04T22:17:41.207038+00:00'"/> -->

		<xsl:variable name="year" select="substring($date,1,4)"/>
		<xsl:variable name="day" select="substring($date,9,2)"/>
		<xsl:variable name="monthName2" select="substring-before(substring-after($date, '-'), '-')"/>
		<xsl:variable name="time" select="substring($date,12,8)"/>
<!-- 		
		<xsl:variable name="m" select="(floor(substring($date,6,2)) - 14) mod 12"/>
		<xsl:variable name="y" select="$year"/>
		<xsl:variable name="C" select="$year div 100"/>
		<xsl:variable name="weekday" select="($day + floor((31 * $m) div 12) - (2*$C) + $y + floor($y div 4) + floor($C div 4)) mod 7"/> -->
		<!-- <xsl:variable name="weekday" select="($day + floor((2.6 * $m) - 0.2) - (2*$C) + $y + floor($y div 4) + floor($C div 4)) mod 7"/> -->
		<!-- <xsl:variable name="weekday2" select="($day + floor((31 * $m) div 12) - floor($y div 100) + $y + floor($y div 4) + floor($y div 400)) mod 7"/> -->
		
		<xsl:variable name="a" select="floor((14 - round($monthName2)) div 12)"/>
		<xsl:variable name="m" select="round(substring($date,6,2)) + 12 * $a - 2"/>
		<xsl:variable name="y" select="round($year) - $a"/>
		<xsl:variable name="weekday" select="($day + floor((31 * $m) div 12) - floor($y div 100) + $y + floor($y div 4) + floor($y div 400)) mod 7"/>

		<xsl:variable name="weekName" select="substring('SunMonTueWedThuFriSat', 3 * $weekday + 1, 3)"/>
		<xsl:variable name="week_name">
			<xsl:choose>
				<xsl:when test="$weekday = 0">Sunday</xsl:when>
				<xsl:when test="$weekday = 1">Monday</xsl:when>
				<xsl:when test="$weekday = 2">Tuesday</xsl:when>
				<xsl:when test="$weekday = 3">Wed</xsl:when>
				<xsl:when test="$weekday = 4">Thursday</xsl:when>
				<xsl:when test="$weekday = 5">Friday</xsl:when>
				<xsl:when test="$weekday = 6">Saturday</xsl:when>
				<xsl:otherwise>
					error: <xsl:value-of select="$weekday"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>

		<!-- Wed, 02 Oct 2002 08:00:00 EST -->
		<!-- <xsl:variable name="day" select="substring-before(substring-after($date, ' '), ' ')"/>
		<xsl:variable name="day2" select="concat(translate(substring($day,1,1), '0', ''), substring($day,2,1))"/>
		<xsl:variable name="monthName" select="substring-before(substring-after(substring-after($date, ' '), ' '), ' ')"/>
		<xsl:variable name="year" select="substring-before(substring-after(substring-after(substring-after($date, ' '), ' '), ' '), ' ')"/> -->
		<!-- <xsl:variable name="month2" select="('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Okt','Nov','Dez')[2]"/> -->
		<!-- <xsl:variable name="monthName3" select="('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')"/>
		<xsl:variable name="monthName4" select="$monthName3[2]"/> -->
		<xsl:variable name="monthName" select="substring('JanFebMarAprMayJunJulAugSepOctNovDec', 3 * ($monthName2 - 1) + 1, 3)"/>
		<!-- <xsl:variable name="month3" select="$month2[2]"/> -->
		<!-- <xsl:variable name="month3" select="$month2[round(substring($date,6,2))-10]"/> -->
		<xsl:variable name="month">
			<xsl:choose>
				<xsl:when test="$monthName = 'Jan'">January</xsl:when>
				<xsl:when test="$monthName = 'Feb'">February</xsl:when>
				<xsl:when test="$monthName = 'Mar'">March</xsl:when>
				<xsl:when test="$monthName = 'Apr'">April</xsl:when>
				<xsl:when test="$monthName = 'May'">May</xsl:when>
				<xsl:when test="$monthName = 'Jun'">June</xsl:when>
				<xsl:when test="$monthName = 'Jul'">July</xsl:when>
				<xsl:when test="$monthName = 'Aug'">August</xsl:when>
				<xsl:when test="$monthName = 'Sep'">September</xsl:when>
				<xsl:when test="$monthName = 'Oct'">October</xsl:when>
				<xsl:when test="$monthName = 'Nov'">November</xsl:when>
				<xsl:when test="$monthName = 'Dec'">Dec</xsl:when>
				<xsl:otherwise>
					NA
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:value-of select="concat($weekName, ', ', $day, ' ',$monthName,  ' ', $year, ' ', $time)"/>
	</xsl:template>
</xsl:stylesheet>

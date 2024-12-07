<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:atom="http://www.w3.org/2005/Atom">
	<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:key name="groupByMonth" match="atom:entry" use="substring(atom:published,6,2)"/>
	<xsl:template match="/">
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<meta name="referrer" content="unsafe-url" />
		<title><xsl:value-of select="/atom:feed/atom:title"/></title>
		<!-- <link rel="stylesheet" href="/layouts/water.min.css" /> -->
		<link rel="stylesheet" href="\layouts\hack.css" />
		<link href="\layouts\main.css" rel="stylesheet" type="text/css" />
		<link href="\layouts\nunito_sans.css" rel="stylesheet" type="text/css" />
	</head>
	<body>

	<div class="NavBackground"></div>
    <div>
      <nav>
        <img class="ProfileImage" src="\images\profile.png" />
        <label class="  NavTitle">Waste of Cyberspace</label>
        <hr/>
        <a class="sidebar" href="\pages\home">Home</a>
        <a class="sidebar" href="\pages\posts">Posts</a>
        <a class="sidebar" href="\pages\projects">Projects</a>
        <a class="sidebar" href="\pages\subscribe">Subscribe</a>
        <hr/>
        <a class="sidebar" href="#Feed-Posts">Feed Posts</a>
      </nav>
    </div>

	<div class="ArticleParent" style="float:right;">
      <article>
        <div class="Post-parent">
          <div class="Post">

		  [<br/>
		  <xsl:for-each select= "/atom:feed/atom:entry[generate-id()=generate-id(key('groupByMonth', substring(atom:published,6,2)))]">
			<!-- <xsl:variable name="Shipment" select="key('groupByMonth', substring(atom:published,6,2))"/> -->
			"<xsl:value-of select="atom:title"/>"-<xsl:value-of select="substring(atom:published,6,2)"/>
			<xsl:variable name="month_u" select="substring(atom:published,6,2)"/>
			    <h3><xsl:value-of select="$month_u"/></h3>
			<xsl:for-each select="/atom:feed/atom:entry[substring(atom:published,6,2)=$month_u]">
				<!-- <xsl:if test="substring(atom:published,6,2) = $month_u"> -->
					TITLE: <xsl:value-of select="atom:title"/><br/>
				<!-- </xsl:if> -->
			</xsl:for-each>
			<br/>
			<!-- <xsl:value-of select="$Shipment/atom:title"/> -->
			<!-- <xsl:for-each select="$Shipment">
				<xsl:value-of select="$Shipment"/>
				<hr/>
			</xsl:for-each> -->
		  </xsl:for-each>
		  ]<br/>

		  [
		  <xsl:for-each select= "/atom:feed/atom:entry[generate-id()=generate-id(key('groupByMonth', substring(atom:published,6,2)))]">
			<!-- <xsl:variable name="Shipment" select="key('groupByMonth', substring(atom:published,6,2))"/> -->
			<!-- "<xsl:value-of select="atom:title"/>"-<xsl:value-of select="substring(atom:published,6,2)"/> -->
			<xsl:variable name="month_u" select="substring(atom:published,6,2)"/>
			    <h3><xsl:value-of select="$month_u"/></h3>
			<xsl:for-each select="/atom:feed/atom:entry">
				<xsl:if test="substring(atom:published,6,2) = $month_u">
					TITLE: <xsl:value-of select="atom:title"/><br/>
				</xsl:if>
			</xsl:for-each>
			<!-- <xsl:value-of select="$Shipment/atom:title"/> -->
			<!-- <xsl:for-each select="$Shipment">
				<xsl:value-of select="$Shipment"/>
				<hr/>
			</xsl:for-each> -->
		  </xsl:for-each>
		  ]
		<xsl:for-each select="/atom:feed/atom:entry">
		  <h1> Group <xsl:value-of select="substring(atom:published, 6,2)" /> <span> (<xsl:value-of select="count(key('groupByMonth', substring(atom:published,6,2)))"/> items)</span></h1>
		  [
		  <xsl:for-each select= "key('groupByMonth', substring(atom:published,6,2))">
			<xsl:variable name="Shipment" select="key('groupByMonth', substring(atom:published,6,2))"/>
			<!-- <xsl:value-of select="$Shipment/atom:published"/> -->
			{
			<xsl:for-each select="$Shipment">
				<xsl:value-of select="$Shipment/@title"/>
				<hr/>
			</xsl:for-each>
			}
			Apple2
		  </xsl:for-each>
		  ]
		  
		  
		  <!-- <span>(-<xsl:value-of select="key('groupByMonth', substring(atom:published,6,2))"/>-)</span> -->
		  <!-- <span>{(<xsl:value-of select="key('groupByMonth', substring(atom:published,6,2))[1]"/>)}</span> -->
		</xsl:for-each>


		<h1>
			<!-- <img alt="feed icon 2" src="{/atom:feed/atom:logo}" style="height:1em;vertical-align:middle;" />&#xa0; -->
			<xsl:value-of select="/atom:feed/atom:title"/> Atom Feed
		</h1>

		<p>
			<xsl:value-of select="/atom:feed/atom:subtitle"/>
		</p>


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

        <!-- <xsl:variable name="last_month" select=""/> -->

        <xsl:variable name="chapters" as="element()*">
			<xsl:for-each select="/atom:feed/atom:entry">
				<xsl:value-of select="substring(atom:published,6,2)"/>
			</xsl:for-each>
		</xsl:variable>

		<h1><a href="#Date">Date</a></h1>
		<hr/>
		<hr/>
		<div class="index-list">
		<ul><xsl:for-each select="/atom:feed/atom:entry">
			<xsl:if test="position() = 1 or substring(atom:published,6,2) != substring($chapters,2 * (position() - 2) + 1,2)">
				<h2 style="margin-left: -0.5rem;"><xsl:value-of select="substring(atom:published,1,4)"/></h2>
				<!-- <ul> -->
            </xsl:if>
			<li style="display: block ruby;">
			<span class="highlighted" title="2024-11-18T15:10:57+00:00">Nov 18</span>
			<details><summary>
				<a>
				<xsl:attribute name="href">
					<xsl:value-of select="atom:id"/>
				</xsl:attribute>
				<xsl:value-of select="atom:title"/>
				</a>
				<!-- <xsl:value-of select="atom:updated" /> -->
				<!-- <xsl:value-of select="format-date(atom:published,'[D01].[M01].[Y0001]')" /> -->
				<!-- <xsl:value-of select="atom:published" /> -->
				<!-- <xsl:call-template name="format-date-string">
					<xsl:with-param name="date" select="atom:published"/>
					<xsl:with-param name="mask">mmm ddd d</xsl:with-param>
				</xsl:call-template> -->
				<div style="float: right;">
				<xsl:call-template name="format-date">
				    <xsl:with-param name="date" select="atom:published"/>
				</xsl:call-template>
				</div>
				</summary>

                <pre>
				<!-- <xsl:text > -->
				<xsl:choose>
					<xsl:when test="atom:content">
						<xsl:value-of select="atom:content" disable-output-escaping="yes"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="atom:summary" disable-output-escaping="yes"/>
					</xsl:otherwise>
				</xsl:choose>
				<!-- </xsl:text> -->
				</pre>

				</details></li>
		</xsl:for-each></ul>
		</div>

		        </div>
				<footer>
            <p>
              <a href="404-changelog.dj.txt">Source</a> | 
              <a href="404">Latest</a>
			<span style="float: right; padding-right: 1rem; color: grey;">Unless stated otherwise, all content on this feed is published under CC-BY-SA. All code on this site is available under the MPL.</span>
            </p>
          </footer>
		        </div>
      </article>
    </div>
	</body>
</html>
	</xsl:template>

	<xsl:template name="format-date">
		<xsl:param name="date"/>
		<!-- Expected date format: 2024-12-04T22:17:41.207038+00:00 -->
		<xsl:variable name="year" select="substring($date,1,4)"/>
		<xsl:variable name="month" select="substring($date,6,2)"/>
		<xsl:variable name="day" select="substring($date,9,2)"/>
		<xsl:variable name="time" select="substring($date,12,8)"/>
		<!-- Get the abbreviated month name -->
		<xsl:variable name="monthName" select="substring('JanFebMarAprMayJunJulAugSepOctNovDec', 3 * ($month - 1) + 1, 3)"/>

		<!-- Get the abbreviated week day -->
		<xsl:variable name="a" select="floor((14 - round($month)) div 12)"/>
		<xsl:variable name="m" select="round(substring($date,6,2)) + 12 * $a - 2"/>
		<xsl:variable name="y" select="round($year) - $a"/>
		<xsl:variable name="weekday" select="($day + floor((31 * $m) div 12) - floor($y div 100) + $y + floor($y div 4) + floor($y div 400)) mod 7"/>
		<xsl:variable name="weekName" select="substring('SunMonTueWedThuFriSat', 3 * $weekday + 1, 3)"/>

		<xsl:value-of select="concat($weekName, ', ', $day, ' ',$monthName,  ' ', $year, ' ', $time)"/>
	</xsl:template>
</xsl:stylesheet>

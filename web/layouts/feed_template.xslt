<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes" />
  <xsl:key name="groupByYear" match="atom:entry" use="substring(atom:published,1,4)" />
  <xsl:key name="groupByYear" match="/rss/channel/item"
    use="substring-before(substring-after(substring-after(substring-after(pubDate, ' '), ' '), ' '), ' ')" />

  <xsl:template match="/">
    <!-- The page HTML -->
  </xsl:template>

  <xsl:template name="list-feeds">
    <!-- A list of all entries -->
    <!-- Loop over each year once -->
    <xsl:variable name="entries_atom" select="/atom:feed/atom:entry[generate-id()=generate-id(key('groupByYear', substring(atom:published,1,4)))]" />
    <xsl:variable name="entries_rss" select="/rss/channel/item[generate-id()=generate-id(key('groupByYear', substring-before(substring-after(substring-after(substring-after(pubDate, ' '), ' '), ' '), ' ')))]" />
    <xsl:for-each select="$entries_atom | $entries_rss">
        <xsl:sort select="position()" data-type="number" order="descending"/>

        <xsl:variable name="year_group">
            <xsl:value-of select="substring(atom:published,1,4)" />
            <xsl:value-of select="substring-before(substring-after(substring-after(substring-after(pubDate, ' '), ' '), ' '), ' ')" />
        </xsl:variable>

        <h2>
          <xsl:attribute name="id"><xsl:value-of select="$year_group"/></xsl:attribute>
          <a>
            <xsl:attribute name="href">#<xsl:value-of select="$year_group"/></xsl:attribute>
            <xsl:value-of select="$year_group"/>
          </a>
        </h2>
        <div class="index-list">
            <ul>
                <!-- Only list entries with matching years -->
                <xsl:variable name="year_entries_atom" select="/atom:feed/atom:entry[substring(atom:published,1,4)=$year_group]" />
                <xsl:variable name="year_entries_rss" select="/rss/channel/item[substring-before(substring-after(substring-after(substring-after(pubDate, ' '), ' '), ' '), ' ')=$year_group]" />
                <xsl:for-each
                    select="$year_entries_atom | $year_entries_rss">
                    <li>
                        <label>
                            <!-- Date label -->
                            <xsl:if test="atom:published">
                                <xsl:call-template name="format-date-atom">
                                    <xsl:with-param name="date" select="atom:published" />
                                </xsl:call-template>
                            </xsl:if>
                            <xsl:if test="pubDate">
                                <xsl:call-template name="format-date-rss">
                                    <xsl:with-param name="date" select="pubDate" />
                                </xsl:call-template>
                            </xsl:if>
                            <!-- Title -->
                            <a>
                              <xsl:attribute name="href">
                                <xsl:value-of select="atom:link/@href" />
                                <xsl:value-of select="link" />
                              </xsl:attribute>
                              <xsl:value-of select="atom:title" />
                              <xsl:value-of select="title" />
                            </a>
                        </label>
                    </li>
                </xsl:for-each>
            </ul>
        </div>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="format-date-atom">
    <!-- Convert raw Atom date to label -->
    <!-- Expected date format: 2024-12-04T22:17:41.207038+00:00 -->
    <xsl:param name="date" />
    <xsl:variable name="month" select="substring($date,6,2)" />
    <xsl:variable name="day" select="substring($date,9,2)" />
    <xsl:variable name="monthName"
      select="substring('JanFebMarAprMayJunJulAugSepOctNovDec', 3 * ($month - 1) + 1, 3)" />
    <span class="highlighted">
      <xsl:attribute name="title"><xsl:value-of select="$date" /></xsl:attribute>
      <xsl:value-of select="concat($monthName,  ' ', $day)" />
    </span>
  </xsl:template>

  <xsl:template name="format-date-rss">
    <!-- Convert raw RSS date to label -->
    <!-- Expected date format: Mon, 18 Nov 2024 15:10:57 +0000 -->
    <xsl:param name="date" />
    <xsl:variable name="monthName"
      select="substring-before(substring-after(substring-after(pubDate, ' '), ' '), ' ')" />
    <xsl:variable name="day" select="substring-before(substring-after(pubDate, ' '), ' ')" />
    <span class="highlighted">
      <xsl:attribute name="title"><xsl:value-of select="$date" /></xsl:attribute>
      <xsl:value-of select="concat($monthName,  ' ', $day)" />
    </span>
  </xsl:template>

</xsl:stylesheet>
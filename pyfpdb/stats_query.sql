
                     select  p.name                                                          AS hgametypeid
                            ,p.name                                                           AS pname
                            ,gt.base
                            ,gt.category                                                            AS category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name                                                                 AS name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            /*,<hcgametypeId>                                                       AS gtid*/
                            ,gt.base                                                             AS plposition
                            ,count(1)                                                               AS n
                            ,100.0*sum(cast(hp.street0VPI as integer))/count(1)             AS vpip
                            ,100.0*sum(cast(hp.street0Aggr as integer))/count(1)            AS pfr
                            ,case when sum(cast(hp.street0_3Bchance as integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as integer))/sum(cast(hp.street0_3Bchance as integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.raiseFirstInChance as integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as integer)) / 
                                       sum(cast(hp.raiseFirstInChance as integer))
                             end                                                                    AS rfi
                            ,case when sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as integer)
                                           when '0' then cast(hp.raiseFirstInChance as integer)
                                           when '1' then cast(hp.raiseFirstInChance as integer)
                                           else 0
                                           end
                                          ) = 0 then -999
                                  else 100.0 * 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raisedFirstIn as integer)
                                           when '0' then cast(hp.raisedFirstIn as integer)
                                           when '1' then cast(hp.raisedFirstIn as integer)
                                           else 0
                                           end
                                          ) / 
                                       sum(case hp.position
                                           when 'S' then cast(hp.raiseFirstInChance as integer)
                                           when '0' then cast(hp.raiseFirstInChance as integer)
                                           when '1' then cast(hp.raiseFirstInChance as integer)
                                           else 0
                                           end
                                          )
                             end                                                                    AS steals
                            ,100.0*sum(cast(hp.street1Seen as integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as integer))/sum(cast(hp.street1Seen as integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as integer))/sum(cast(hp.sawShowdown as integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as integer))/sum(cast(hp.street1Seen as integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as integer))/sum(cast(hp.street2Seen as integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as integer))/sum(cast(hp.street3Seen as integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as integer))+sum(cast(hp.street2Seen as integer))+sum(cast(hp.street3Seen as integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as integer))+sum(cast(hp.street2Aggr as integer))+sum(cast(hp.street3Aggr as integer)))
                                          /(sum(cast(hp.street1Seen as integer))+sum(cast(hp.street2Seen as integer))+sum(cast(hp.street3Seen as integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as integer))+ sum(cast(hp.street2Calls as integer))+ sum(cast(hp.street3Calls as integer))+ sum(cast(hp.street4Calls as integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as integer)) + sum(cast(hp.street2Aggr as integer)) + sum(cast(hp.street3Aggr as integer)) + sum(cast(hp.street4Aggr as integer)))
                                     /(sum(cast(hp.street1Calls as integer))+ sum(cast(hp.street2Calls as integer))+ sum(cast(hp.street3Calls as integer))+ sum(cast(hp.street4Calls as integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as integer)) + sum(cast(hp.street2Aggr as integer)) + sum(cast(hp.street3Aggr as integer)) + sum(cast(hp.street4Aggr as integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as integer))) +
                                       (sum(cast(hp.street1Calls as integer))+ sum(cast(hp.street2Calls as integer))+ sum(cast(hp.street3Calls as integer))+ sum(cast(hp.street4Calls as integer))) +
                                       (sum(cast(hp.street1Aggr as integer)) + sum(cast(hp.street2Aggr as integer)) + sum(cast(hp.street3Aggr as integer)) + sum(cast(hp.street4Aggr as integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as integer)) + sum(cast(hp.street2CBDone as integer)) + sum(cast(hp.street2CBDone as integer)) + sum(cast(hp.street4CBDone as integer))) 
                                       / (sum(cast(hp.street1CBChance as integer))+ sum(cast(hp.street2CBChance as integer))+ sum(cast(hp.street3CBChance as integer))+ sum(cast(hp.street4CBChance as integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gameTypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in (hp.playerId)
                      and gt.category in ('omahahi')
                      and gt.siteId in (14)
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats between 2 and 10
                      
                      and ( (gt.limitType = 'fl' and gt.bigBlind in (-1) )  or (gt.limitType = 'pl' and gt.bigBlind in (5, 10) )  or (gt.limitType = 'nl' and gt.bigBlind in (-1) ) ) and gt.type = 'ring' 
                      and   datetime(h.startTime)  between '1970-01-02 04:00:00' and '2020-12-13 03:59:59'
                      group by hgameTypeId
                              ,hp.playerId
                              ,gt.base
                              ,gt.category
                              
                              ,plposition
                              ,upper(gt.limitType)
                              ,s.name
                      having 1 = 1 
                      order by hp.playerId
                              ,gt.base
                              ,gt.category
                              
                              ,case gt.base when 'B' then 'B'
                                               when 'S' then 'S'
                                               when '0' then 'Y'
                                               else 'Z'||gt.base
                               end
                              
                              ,upper(gt.limitType) desc
                              ,max(gt.bigBlind) desc
                              ,s.name
                      
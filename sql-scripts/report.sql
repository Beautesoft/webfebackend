Declare @FDate DATETIME
Declare @TDate DATETIME
DECLARE @PayGroup nvarchar(50)
DECLARE @Site nvarchar(50)

SET @FDate=Convert(Datetime,'2021-06-01 00:00:00.000',103)
SET @TDate=Convert(Datetime,'2021-06-10 00:00:00.000',103)
SET @PayGroup = ''
SET @Site = ''


SELECT
    (select distinct Itemsite_Desc from item_sitelist where itemSite_Code=pos_haud.ItemSite_Code) [Outlet],
    pos_haud.ItemSite_Code [site1],
    paytable.gt_group [PayGroup],
    pos_taud.pay_Desc [payTypes],
    Convert(nvarchar,pos_haud.sa_date,103) [payDate],
    pos_haud.SA_TransacNo_Ref [InvoiceRef],
    pos_haud.sa_custno [customerCode],
    pos_haud.sa_custname [customer],
    isnull(pos_daud.dt_itemdesc,'') [ItemName],

    case when (select isactive from GST_Setting)=1
        then
            sum(round(
                    pos_taud.pay_actamt
                      -( Case When pos_taud.pay_type='CN'
                            Then (pos_taud.pay_actamt)
                            Else 0 End
                        )
                      - ( CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                            Then 0
                          Else pos_taud.PAY_GST End
                        )
                      - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                                                                            Then 0
                                                                            Else pos_taud.PAY_GST End
                                                    )
                          )/100  +0 ,
                    3)
                )
        else
            sum( pos_taud.pay_actamt
                    -( Case When pos_taud.pay_type='CN'
                            Then (pos_taud.pay_actamt)
                            Else 0
                        End
                    )
                )
    end [beforeGST],

    sum(Convert(Decimal(19,3),
                Case When pos_taud.pay_type='CN'
                    Then pos_taud.PAY_GST
                    else ( CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                                Then 0
                                Else pos_taud.PAY_GST
                            End
                        )
                end
                )) [GST],

    sum(pos_taud.pay_actamt-( Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End ))   [afterGST]

FROM pos_haud
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate
  And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate
  and paytable.pay_code in (select pay_code from paytable)
  and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0
  And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site
  And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup
group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group,pos_haud.SA_TransacNo_Ref,pos_haud.sa_custno,
         pos_haud.sa_custname,pos_daud.dt_itemdesc
order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc
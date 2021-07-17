Declare @FDate DATETIME
Declare @TDate DATETIME
DECLARE @Site nvarchar(Max)
DECLARE  @Dept nvarchar(Max)
DECLARE  @GroupByStaff  nvarchar(1)
DECLARE  @ShowNonSales nvarchar(1)
DECLARE  @ShowOldBill nvarchar(1)
DECLARE  @ReportType nVarchar(10)

SET @FDate=Convert(Datetime,'2021-06-01 00:00:00.000',103)
SET @TDate=Convert(Datetime,'2021-06-10 00:00:00.000',103)

SET @Site = ''
SET  @Dept = ''
SET  @GroupByStaff  = ''
SET  @ShowNonSales = 'Y'
SET  @ShowOldBill= 'Y'
SET  @ReportType= ''




select Sales_Record.* ,
       ISNULL(Item_Dept.itm_Desc,'') as Dept,
        case when Ttl_actamt.Ttl_actamt = 0
            then 0
            else isnull((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit) ,0)
        end [GT1_proportion_amt],
case when Ttl_actamt.Ttl_actamt = 0 then
0
else
isnull((GT2_actamt.GT2_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit) ,0)
end [GT2_proportion_amt] , IsVoid.IsVoid ,
case when Pay_OldBill.OldBill_Count is null then
0
else
Pay_OldBill.OldBill_Count
end [OldBill_Count],

  case when (@ShowNonSales='Y') then
    case when (Ttl_actamt.Ttl_actamt = 0)  then
     0
     else
     round(isnull((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit),0)+isnull((GT2_actamt.GT2_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit),0),2)
     end
  else
     case when Ttl_actamt.Ttl_actamt = 0 then
	 0
	 else
	 round(isnull((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit),0),2)
	 end
  end
[Amount]
from (select convert(datetime,pos_haud.sa_date,103) [saDate], pos_haud.itemsite_code [outlet], pos_haud.sa_transacno_ref [invoiceRef], pos_daud.sa_transacno, pos_daud.dt_lineno,
case when  (pos_daud.record_detail_type = 'TP SERVICE') then
(select distinct service_itembarcode from treatment where treatment.treatment_parentcode = pos_daud.TopUp_service_trmt_code)
else
pos_daud.dt_itemno
end
[itemCode]
,
case when  (pos_daud.record_detail_type = 'TP SERVICE') then
isnull((select distinct item_name from stock where item_code+ '0000'=(select distinct service_itembarcode from treatment where treatment.treatment_parentcode = pos_daud.TopUp_service_trmt_code)),0)
else
isnull((select distinct item_name from stock where item_code+ '0000'=pos_daud.dt_itemno),'')
end
[itemDesc]
,
pos_daud.record_detail_type,
case when  (pos_daud.record_detail_type = 'TP SERVICE' or pos_daud.record_detail_type = 'TP Product') then
 0
else
pos_daud.dt_qty
end
[Qty] ,
pos_daud.dt_deposit, pos_daud.dt_discamt [Discount]
from pos_haud
LEFT OUTER JOIN pos_daud on pos_haud.sa_transacno = pos_daud.sa_transacno) as Sales_Record

LEFT OUTER JOIN Stock on Stock.Item_code + '0000' = Sales_Record.itemCode

LEFT OUTER JOIN Item_Dept on Stock.Item_Dept = Item_Dept.itm_Code

LEFT OUTER JOIN (SELECT     pos_taud_1.sa_transacno, SUM(pos_taud_1.pay_actamt) AS GT1_actamt
FROM          pos_taud AS pos_taud_1 INNER JOIN
PAYTABLE AS PAYTABLE_1 ON pos_taud_1.pay_type = PAYTABLE_1.pay_code
WHERE      (PAYTABLE_1.GT_Group = 'GT1')
GROUP BY pos_taud_1.sa_transacno) GT1_actamt on GT1_actamt.sa_transacno = Sales_Record.sa_transacno

LEFT OUTER JOIN (SELECT     pos_taud_1.sa_transacno, SUM(pos_taud_1.pay_actamt) AS GT2_actamt
FROM          pos_taud AS pos_taud_1 INNER JOIN
PAYTABLE AS PAYTABLE_1 ON pos_taud_1.pay_type = PAYTABLE_1.pay_code
WHERE      (PAYTABLE_1.GT_Group = 'GT2')
GROUP BY pos_taud_1.sa_transacno) GT2_actamt on GT2_actamt.sa_transacno = Sales_Record.sa_transacno

LEFT OUTER JOIN (SELECT     pos_taud_1.sa_transacno, SUM(pos_taud_1.pay_actamt) AS Ttl_actamt
FROM          pos_taud AS pos_taud_1
GROUP BY pos_taud_1.sa_transacno) Ttl_actamt on Ttl_actamt.sa_transacno = Sales_Record.sa_transacno

LEFT OUTER JOIN (SELECT     pos_haud.sa_transacno, pos_haud.isVoid
FROM          pos_haud ) IsVoid on IsVoid.sa_transacno = Sales_Record.sa_transacno

LEFT JOIN (SELECT     pos_taud.sa_transacno, count(*) as OldBill_Count
FROM          pos_taud where pay_type = 'OB' group by sa_transacno ) Pay_OldBill on Pay_OldBill.sa_transacno = Sales_Record.sa_transacno

Where sadate BETWEEN @FDate AND @TDate
and IsVoid=0
and (Ttl_actamt.Ttl_actamt>0 and ((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0 or (GT2_actamt.GT2_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0))
and (@ShowOldBill='Y' OR (@ShowOldBill='N' AND (Pay_OldBill.OldBill_Count=0 or Pay_OldBill.OldBill_Count is null)))
And ((@Site='') OR ((@Site<>'') And Outlet In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site
And ((@Dept='') OR ((@Dept<>'') And Item_Dept.itm_Desc In (Select Item From dbo.LISTTABLE(@Dept,','))))--Department
ORDER BY SA_TRANSACNO
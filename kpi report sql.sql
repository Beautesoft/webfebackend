
IF OBJECT_ID('tblServiceSetting', 'U') IS NULL 
BEGIN 
Create table tblServiceSetting
([ID] int IDENTITY(1,1) PRIMARY KEY,
ItemCode nvarchar(50) null,ItemName nvarchar(50) null,
FollowUp_Days int null,FollowUp_Group nvarchar(50) null,
Count_AfterPurchase bit null,Count_AfterTD bit null,
FollowUp_WarningDays int null,ItemSite_Code nvarchar(50) null,
SDATE datetime null,PW_UserLogin nvarchar(50))
END



--create table paydesctab(paydesc nvarchar(50) null)

---------------
--alter table Title
--Add logo_pic nvarchar(200)

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'GETLOGO')
BEGIN
DROP PROCEDURE GETLOGO
END
GO
CREATE PROCEDURE GETLOGO
AS
select Trans_Logo,Trans_H1,Trans_H2,Trans_Footer1,Trans_Footer1,Trans_Footer2,Trans_Footer3,Trans_Footer4,logo_pic from Title
GO


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyVsUnearndRevenue')
BEGIN
DROP PROCEDURE Web_DailyVsUnearndRevenue
END
GO
CREATE PROCEDURE Web_DailyVsUnearndRevenue
@FromDate Varchar(10),  
@ToDate Varchar(10),  
@Site Varchar(10),  
@Type Varchar(10)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)  
  
IF OBJECT_ID('tempdb.#Data_All') IS NOT NULL DROP TABLE #Data_All  
  
  
  
Select * from (  
Select   
Convert(Varchar(10),T0.Treatment_Date,103) [OperationDate],  
T1.ItemSite_Desc [Outlet],  
T0.Cust_Name [Customer],  
T2.SA_TransacNo_Ref [Invoice],  
T4.SA_TransacNo_Ref [TDInvoice],  
T0.Course [Course],  
0 [Price_Expired],  
T0.Price [Price_Total],  
T0.Treatment_Code [TreatmentCode],  
ISNULL((Select Helper_Name+',' from Item_helper X Where X.Item_Code=T0.Treatment_Code FOR XML PATH('')),'') [Staff],  
T0.Status [Status],  
T0.Treatment_No+'/'+(Select Max(X.Treatment_No) from Treatment X Where X.Treatment_ParentCode=T0.Treatment_ParentCode) [Session],  
0 [Count_Expired],  
1 [Count_Total]  
from Treatment T0 JOIN Item_SiteList T1 ON T1.ItemSite_Code=T0.Site_Code   
JOIN pos_haud T2 ON T2.sa_transacno=T0.sa_transacno  
Left JOIN Treatment_Account T3 ON T0.Treatment_Code=T3.sa_transacno  
Left JOIN pos_haud T4 ON T4.sa_transacno=T2.sa_transacno  
Where T0.Site_Code=@Site  and T0.Treatment_Date>=@FDate and T0.Treatment_Date<=@TDate and T0.Status='Done'  
UNION ALL  
Select   
Convert(Varchar(10),T0.Treatment_Date,103) [OperationDate],  
T1.ItemSite_Desc [Outlet],  
T0.Cust_Name [Customer],  
T2.SA_TransacNo_Ref [Invoice],  
T4.SA_TransacNo_Ref [TDInvoice],  
T0.Course [Course],  
T0.Price [Price_Expired],  
0 [Price_Total],  
T0.Treatment_Code [TreatmentCode],  
ISNULL((Select Helper_Name+',' from Item_helper X Where X.Item_Code=T0.Treatment_Code FOR XML PATH('')),'') [Staff],  
'Expired' [Status],  
T0.Treatment_No+'/'+(Select Max(X.Treatment_No) from Treatment X Where X.Treatment_ParentCode=T0.Treatment_ParentCode) [Session],  
1 [Count_Expired],  
0 [Count_Total]  
from Treatment T0 JOIN Item_SiteList T1 ON T1.ItemSite_Code=T0.Site_Code   
JOIN pos_haud T2 ON T2.sa_transacno=T0.sa_transacno  
Left JOIN Treatment_Account T3 ON T0.Treatment_Code=T3.sa_transacno  
Left JOIN pos_haud T4 ON T4.sa_transacno=T2.sa_transacno  
Where T0.Site_Code=@Site  and T0.Treatment_Date>=@FDate and T0.Treatment_Date<=@TDate  
And CONVERT(Datetime,expiry,112)=CONVERT(Datetime,Getdate(),112))X  
Order By Convert(DateTime,X.OperationDate,103)  


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_TopSalesServiceReport1')
BEGIN
DROP PROCEDURE Web_TopSalesServiceReport1
END
GO
CREATE  PROCEDURE Web_TopSalesServiceReport1    
 @FromDate nvarchar(10),    
 @ToDate nvarchar(10),     
 @Site nvarchar(Max),    
 @Dept nvarchar(Max),     
 @FItem nvarchar(255),     
 @TItem nvarchar(255),     
 @ShowFOC  nvarchar(1),    
 @SortBy  nvarchar(10)    
     
AS    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate + ' 00:00:00.000',103)    
SET @TDate=Convert(Datetime,@ToDate + ' 23:59:59.000',103)    
SELECT pos_haud.ItemSIte_Code,pos_daud.dt_no, pos_daud.mac_code, pos_daud.sa_date, pos_daud.sa_time, 
pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice, pos_daud.dt_amt, 
pos_daud.dt_qty, pos_daud.dt_discAmt,  
pos_daud.dt_discPercent, pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,
 pos_daud.dt_StaffName, pos_daud.dt_Reason,  
pos_daud.dt_DiscUser, pos_daud.dt_ComboCode, pos_daud.ItemSite_Code, pos_daud.dt_LineNo, 
pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment, pos_daud.Next_Appt, 
pos_daud.dt_TransacAmt, pos_daud.dt_deposit,  
pos_daud.Appt_Time, pos_daud.Hold_Item_Out, pos_daud.Issue_Date, pos_daud.Hold_Item, pos_daud.HoldItemQty, 
pos_daud.ST_Ref_TreatmentCode,  
pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done, pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,  
pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name, pos_daud.Trmt_Done_ID, 
pos_daud.Trmt_Done_Type,  
pos_daud.TopUp_Service_Trmt_Code, pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, 
pos_daud.TopUp_Prepaid_Type_Code,  
pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus, pos_daud.Deduct_Commission, 
pos_daud.Deduct_comm_refLine,  
pos_daud.GST_Amt_Collect,  pos_daud.TopUp_Prepaid_POS_Trans_LineNo,  
pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt,  
pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, pos_daud.dt_GrossAmt,  pos_daud.dt_TopUp_Old_Outs_Amt,  
pos_daud.dt_TopUp_New_Outs_Amt, pos_daud.dt_TD_Tax_Amt, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name,  
pos_haud.sa_status AS SA_STATUS, pos_haud.SA_TransacNo_Ref, StockInfo.item_code, StockInfo.Rpt_Code, 
StockInfo.BrandDesc, StockInfo.RangeDesc,  
StockInfo.DeptDesc, StockInfo.Item_Div, StockInfo.Item_Type  
FROM pos_daud INNER JOIN  
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN  
(SELECT Stock.item_code, Stock.Rpt_Code, Item_Brand.itm_desc AS BrandDesc, Item_Range.itm_desc AS RangeDesc, 
Item_Dept.itm_desc AS DeptDesc,  
Stock.Item_Div, Stock.Item_Type  
FROM Item_Range RIGHT OUTER JOIN  
Item_Dept RIGHT OUTER JOIN  
Stock ON Item_Dept.itm_code = Stock.Item_Dept LEFT OUTER JOIN  
Item_Brand ON Stock.item_Brand = Item_Brand.itm_code ON Item_Range.itm_code = Stock.Item_Range  
WHERE (Stock.Item_Type <> 'Package')) AS StockInfo ON pos_daud.dt_itemno = StockInfo.item_code + '0000'  
WHERE (LEFT(pos_daud.dt_itemno, 1) = '3')   
AND (pos_haud.sa_date >=@FDate) AND (pos_haud.sa_date <= @TDate)  
--AND (pos_haud.ItemSite_Code >= 'IP01') AND (pos_haud.ItemSite_Code <= 'IP01')   
And ((@Site='') OR ((@Site<>'')  And  pos_haud.ItemSIte_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Dept     
AND (pos_haud.sa_status <> 'PP')  
ORDER BY dt_itemdesc,sa_transacno_ref


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionByPayType')
BEGIN
DROP PROCEDURE Web_SaleCollectionByPayType
END
GO
CREATE  PROCEDURE Web_SaleCollectionByPayType  
@FromDate Varchar(10),  
@ToDate Varchar(10),  
@Site Varchar(max),  
@Type Varchar(10),  
@PayMode Varchar(max)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)  
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport  
  
IF OBJECT_ID('tempdb.#a1') IS NOT NULL DROP TABLE #a1  
IF OBJECT_ID('tempdb.#a2') IS NOT NULL DROP TABLE #a2  
IF OBJECT_ID('tempdb.#a3') IS NOT NULL DROP TABLE #a3  
  
select  pos_haud.sa_transacno_ref,pos_daud.dt_StaffName into #a1 from pos_haud inner join pos_daud on 
pos_haud.sa_transacno=pos_daud.sa_transacno  
Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate   
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
  
  
SELECT sa_transacno_ref, staffName = STUFF((SELECT distinct N', ' + dt_StaffName   
  FROM dbo.#a1 AS p2  
   WHERE p2.sa_transacno_ref = p.sa_transacno_ref   
   FOR XML PATH(N''), TYPE).value(N'.[1]', N'nvarchar(max)'), 1, 2, N'') into #a2  
FROM dbo.#a1 AS p  
GROUP BY sa_transacno_ref  
ORDER BY sa_transacno_ref;  
  
  
select  pos_haud.sa_transacno_ref,count(pos_daud.dt_deposit) as Tpcount,sum(pos_daud.dt_deposit) as Tpdeposit into #a3 from   
pos_haud inner join pos_daud on pos_haud.sa_transacno=pos_daud.sa_transacno  
Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate    
and Record_Detail_Type like '%TP%'  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
group by pos_haud.sa_transacno_ref  
  
Select X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],  
  
--STRING_SPLIT (X.payTypes,',') [payTypes],  
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],  
X.payTypes [payTypes],  
(case when X.[Group]='GT1' then 'Sales' else 'Non-Sales' end) as SalesGroup,  
X.ItemSite_Code [siteCode],  
X.ItemSite_Desc [siteName],  
X.RcvedBy [RcvedBy],  
X.servedBy [servedBy],  
isnull(X.Tpcount,0) [Tpcount],  
isnull(X.Tpdeposit,0) [Tpdeposit],  
isnull(SUM(X.amt),0) [amt],  
isnull(SUM(X.payCN),0) [payCN],  
isnull(SUM(X.payContra),0) [payContra],  
isnull(SUM(X.grossAmt),0) [grossAmt],  
isnull(MAX(X.taxes),0) [taxes],  
isnull(SUM(X.gstRate),0) [gstRate],  
isnull(SUM(X.netAmt),0) [netAmt],  
isnull(SUM(X.BankCharges),0) [BankCharges],  
isnull(SUM(X.comm),0) [comm],  
isnull(SUM(X.total),0) total    
from (  
SELECT   
--pos_haud.sa_date [payDate],    
--CAST (pos_haud.sa_date AS DATE) [payDate],   
convert (varchar,pos_haud.sa_date,103)[payDate],   
Customer.Cust_name [customer],    
pos_haud.SA_TransacNo_Ref [invoiceRef],   
pos_haud.sa_transacno [payRef],  
Customer.Cust_Refer [CustRef],  
pos_taud.pay_Desc [payTypes],   
pos_haud.cas_name [RcvedBy],  
#a2.staffName as [servedBy],  
#a3.Tpcount as [Tpcount],  
#a3.Tpdeposit as [Tpdeposit],  
pos_taud.pay_actamt  [amt] ,   
0 [payContra],  
paytable.GT_Group [Group],  
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  
pos_taud.PAY_GST [taxes],  
Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 
Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  
0 [comm],  
--isnull(bank_charges,0) [BankCharges],  
round((isnull(bank_charges,0) * pos_taud.pay_actamt)/100 ,2) as [BankCharges],  
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - isnull(bank_charges,0)+0 [total],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then 
(pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - round((isnull(bank_charges,0) * pos_taud.pay_actamt)/100 ,2) +0 [total],  
pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc  
FROM pos_haud   
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code   
INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code   
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE  
LEFT JOIN #a2 on pos_haud.SA_TransacNo_Ref=#a2.SA_TransacNo_Ref  
LEFT JOIN #a3 on pos_haud.SA_TransacNo_Ref=#a3.SA_TransacNo_Ref  
Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate --And pos_haud.ItemSite_Code=@Site  
--and pos_haud.SA_TransacNo_Type='Receipt'  
--and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )   
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
And ((@PayMode='') OR ((@PayMode<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayMode,',')))) --pay  
)X  
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,[payRef],[CustRef],X.[Group],  
X.[RcvedBy],X.[servedBy],X.[Tpcount],X.[Tpdeposit]  

-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'getstocklist')
BEGIN
DROP PROCEDURE getstocklist
END
GO
create procedure getstocklist  
 @Dept nvarchar(255),                                      
 @Range nvarchar(255),                                       
 @Brand nvarchar(255),                                      
 @FItem nvarchar(255),                                      
 @TItem nvarchar(255),                                      
 @ShowInactive nvarchar(1)                                    
   
AS  
SELECT  distinct Stock.Item_Name [ItemName],Stock.ITEM_CODE [ItemCode],  
item_div.itm_desc [itm_desc],item_brand.itm_desc [site],item_range.itm_desc [Product],  
ITEM_UOMPRICE.ITEM_UOM [UOM],ITEM_UOMPRICE.ITEM_PRICE [Cost] from Stock INNER JOIN   
    Item_StockList ON Stock.item_code = Item_StockList.Item_Code  INNER JOIN                                                                           
    Item_Div ON Stock.Item_Div = Item_Div.itm_code INNER JOIN                                       
    Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code  INNER JOIN                                       
    Item_Brand ON Stock.item_Brand = Item_Brand.itm_code LEFT OUTER JOIN                                       
    Item_Range ON Stock.Item_Range = Item_Range.itm_code RIGHT OUTER JOIN                                       
    ITEM_BATCH ON Item_StockList.ItemSite_Code = ITEM_BATCH.SITE_CODE AND Item_StockList.Item_Code = ITEM_BATCH.ITEM_CODE INNER JOIN                                       
    ITEM_UOMPRICE ON ITEM_BATCH.UOM = ITEM_UOMPRICE.ITEM_UOM AND ITEM_BATCH.ITEM_CODE = ITEM_UOMPRICE.ITEM_CODE  RIGHT OUTER JOIN                                       
    Item_SiteList ON  ITEM_BATCH.SITE_CODE = Item_SiteList.ItemSite_Code                                        
      
 where   
                                 
  ((@FItem='Select') OR Stock.item_desc >= @FItem) AND ((@TItem='Select') OR  Stock.item_desc <= @TItem) --Item                                      
 And ((@Dept='') OR ((@Dept<>'')  And  item_dept.itm_code In (Select Item From dbo.LISTTABLE(@Dept,',')))) --Dept                                   
 And ((@Brand='') OR ((@Brand<>'')  And item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand                                      
 And ((@Range='') OR ((@Range<>'')  And item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range                                                          
 And ((@ShowInactive='Y') OR Stock.Item_Isactive =1)             
           
 And Stock.Item_Div Between '1' And  '2'                                      
Go
-------------
-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Chkinsstktrn')
BEGIN
DROP PROCEDURE Chkinsstktrn
END
GO
create procedure Chkinsstktrn    
 @Site nvarchar(255),                                         
 @itemcode nvarchar(50),    
 @date1 nvarchar(50)    
AS    
Declare @FDate DATETIME  
SET @FDate=Convert(Datetime,@date1,103) 
if isnull((Select count(*) from stktrn where store_no=@Site and itemcode=@itemcode + '0000' and 
Convert(date,trn_Date,103)<=@FDate),0) = 0    
begin    
insert into stktrn(trn_post,trn_date,post_time,itemcode,store_no,trn_qty,trn_balqty,trn_balcst,trn_amt,trn_cost,item_uom)     
values (Convert(date,@date1,103),Convert(date,@date1,103),'000000',@itemcode+'0000',@Site,0,0,0,0,0,'')    
End 
-------------
-------------
-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'TreatmentDetails')
BEGIN
DROP PROCEDURE TreatmentDetails
END
GO
CREATE PROCEDURE TreatmentDetails
 -- Add the parameters for the stored procedure here    
 @StartDate datetime,    
 @EndDate datetime,    
 @siteCode VARCHAR(4),    
 @CustCode VARCHAR(MAX),    
 @PayMode VARCHAR(MAX)    
AS    
BEGIN    
    
--select * from ReportTmpMData     
--select * from ReportTmpMData where string8 = 'TJY07T1100447'    
--select * from ReportTmpMData  where double2 != double3+double4+double5    
--select * from fmspw where pw_userlogin = 'sequoia'    
--select date2, * from ReportTmpMData where string13 = 'nsjy05t1108412' order by string4    
--select top 100 date2, * from ReportTmpMData where date2 = '2019/01/11'     
--select top 100 date2, * from ReportTmpMData where string13 like '%TDJY07T1108116%'    
--select * from treatment where treatment_parentcode = 'TRMTJY05T1100014'  order by treatment_date    
--select * from treatment where sa_transacno = 'TJY07T1100447'    
--select * from pos_haud where sa_transacno = 'TJY07T1100447'    
--select * from treatment_account where treatment_parentcode = 'TRMTJY07T1103352'     
--select * from ReportTmpMData where double2 <= (double3 + double4+ double5)    
    
truncate table ReportTmpMData    
    
INSERT INTO ReportTmpMData     
(    
Date1    
 ,Date3    
 ,Date4    
 ,Date5    
 ,Double1    
 ,DOUBLE2    
 ,DOUBLE3    
 ,DOUBLE4    
 ,double5    
 ,DOUBLE6    
 ,DOUBLE7    
 , double8    
 , double9    
 , double10    
 , string1     
 ,STRING2    
 , STRING3    
 , string4    
 , String5    
 , String6    
 , STRING7     
 , STRING8    
 , STRING9    
 , STRING10    
    , STRING11    
 , STRING12    
 ,double11    
 , double12    
 ,double15    
 , STRING13    
 ,date2    
)    
select    
Date1    
 ,Date3    
 ,Date4    
 ,Date5    
 ,Double1    
 ,DOUBLE2    
 ,DOUBLE3    
 ,DOUBLE4    
 ,double5    
 ,DOUBLE6    
 ,DOUBLE7    
 , double8    
 , double9    
 , double10    
 , string1     
 ,STRING2    
 , STRING3    
 , string4    
 , String5    
 , String6    
 , STRING7     
 , STRING8    
 , STRING9    
 , STRING10    
    , STRING11    
 , STRING12    
 ,double11    
 , double12    
 ,double15    
 , STRING13    
 ,date2    
 from    
(    
 Select     
  max(Date1) as Date1    
 ,dateadd(day, 730, max(Date1)) as Date3    
 ,max(Date1) as Date4    
 ,(case when max(date5) is null then getdate() else max(date5) end ) as date5    
 ,max(Double1) as Double1    
 ,max(DOUBLE2) as DOUBLE2    
 ,max(DOUBLE3) as DOUBLE3    
 ,max(DOUBLE4) as DOUBLE4    
 ,max(DOUBLE2) - max(DOUBLE3) - max(DOUBLE4) as DOUBLE5    
 ,round(max(DOUBLE6) ,2) as DOUBLE6    
 ,round(max(DOUBLE7) ,2) as DOUBLE7    
 ,round(sum(double8) ,2) as double8    
 ,(case when round( max(double6) - sum(double8),2) >= 0 then round( max(double6) - sum(double8),2) else 0 end) as double9    
 ,round( sum(double10),2) as double10    
 ,max(string1) as string1     
 ,max(STRING2) as STRING2    
 ,max(STRING3) as STRING3    
 ,max(c.cust_name) as String4     
 ,max(String5) as String5    
 ,max(String6) as String6    
 ,max(STRING7) as STRING7     
 ,min(STRING8) as STRING8    
 ,max(STRING9) as STRING9    
 ,max(STRING10) as STRING10    
    ,max(STRING11) as STRING11    
 ,max(STRING12) as STRING12    
 ,round((case when sum(double8) + sum(double10) > 0 then sum(double8) + sum(double10) else 0 end ),2) as double11    
 --,round((case when sum(double8) + sum(double10) > 0 then 0 else sum(double8) + sum(double10) end ),2) as double12    
 ,0 as double12    
 ,(case when max(date5) > getdate() then 1 else 0 end ) as double15    
 ,min(ph.sa_transacno_ref) as string13    
 ,(case when min(ph.sa_date) is null then min(date1) else min(ph.sa_date) end ) as date2    
 from (    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,min(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,min(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,min(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,0 as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,0 as DOUBLE54    
 ,sum(Unit_Amount) as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where (pd.sa_Date >= @StartDate AND pd.sa_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,count(t.status) as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,sum(Unit_Amount) as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc not like '%(FOC)%' and t.type != 'FFi' and t.status = 'Done'  and t.type != 'FFd' 
and (T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,0 as DOUBLE3    
 ,count(t.status) as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,sum(Unit_Amount) as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc not like '%(FOC)%' and t.type != 'FFi' and t.status like  '%Cancel%'   and t.type != 'FFd' 
and  (T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,count(t.status) as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,round(sum(Unit_Amount/99),2) as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc not like '%(FOC)%' and t.status = 'Done' and (t.type = 'FFd' or t.type = 'FFi' ) 
and  (T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,0 as DOUBLE3    
 ,count(t.status) as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,sum(Unit_Amount) as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc not like '%(FOC)%' and  t.status like  '%Cancel%'   and  (t.type = 'FFd' or t.type = 'FFi' ) 
and  (T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,count(t.status) as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,0 as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc like '%(FOC)%' and t.status = 'Done' and  
(T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  max(dt_staffno) as STRING11    
 ,max(dt_staffname) as STRING12    
 ,max(TREATMENT_DATE) as Date1    
 ,max(ITEM_CODE) as string1     
 ,max(Course) as STRING2    
 ,max(t.Cust_code) as STRING3    
 ,max(t.Cust_Name) as String4     
 ,max(t.Treatment_Code) String5    
 ,max(Unit_Amount) as Double1    
 ,max(t.sa_transacno) as STRING8    
 ,max(Unit_Amount) as DOUBLE7    
 ,max(ItemSite_Code) as STRING9    
 ,max(ItemSite_Code) as STRING10    
 ,max(Cust_phone2) as STRING7     
 ,count(Times ) as DOUBLE2    
 ,0 as DOUBLE3    
 ,count(t.status) as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(t.treatment_parentcode) as String6    
 ,max(status) as DOUBLE54    
 ,0 as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(type) as type    
 ,max(pd.dt_itemdesc) AS Package_Desc     
 ,max(pd.dt_LineNo) AS dt_LineNo    
 ,max(t.Expiry) as date5    
 from Treatment t    
with (nolock)     
INNER JOIN pos_daud pd ON t.sa_transacno = pd.sa_transacno AND t.dt_LineNo = pd.dt_LineNo     
LEFT OUTER JOIN Customer ON t.Cust_Code = Customer.Cust_code     
where pd.dt_itemdesc like '%(FOC)%' and  t.status like  '%Cancel%'   and  (t.type = 'FFd' or t.type = 'FFi' ) 
and  (T.Treatment_Date >= @StartDate AND T.Treatment_Date <= @EndDate) and t.site_code = @siteCode    
group by t.TREATMENT_parentCODE    
order by t.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  '' as STRING11    
 ,'' as STRING12    
 ,'' as Date1    
 ,'' as string1     
 ,'' as STRING2    
 ,max(ta.Cust_code) as STRING3    
 ,'' as String4     
 ,max(ta.Treatment_Code) String5    
 ,0 as Double1    
 ,max(ta.sa_transacno) as STRING8    
 ,0 as DOUBLE7    
 ,max(ta.Site_Code) as STRING9    
 ,max(ta.Site_Code) as STRING10    
 ,'' as STRING7     
 ,0 as DOUBLE2    
 ,0 as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(ta.treatment_parentcode) as String6    
 ,'' as DOUBLE54    
 ,0 as DOUBLE6    
 ,0 as double8    
 ,0 as double9    
 ,round(sum(Amount),2) as double10    
 ,max(ta.type) as type    
 ,'' AS Package_Desc     
 ,max(ta.dt_LineNo) AS dt_LineNo    
 ,getdate() as date5    
 from Treatment_account ta     
with (nolock)     
where (ta.Type = 'CANCEL' OR ta.Type = 'SALES') and (Ta.sa_Date >= @StartDate AND Ta.sa_Date <= @EndDate)
 and ta.site_code = @siteCode    
group by ta.TREATMENT_parentCODE    
UNION ALL    
Select top 100000    
  '' as STRING11    
 ,'' as STRING12    
 ,'' as Date1    
 ,'' as string1     
 ,'' as STRING2    
 ,max(ta.Cust_code) as STRING3    
 ,'' as String4     
 ,max(ta.Treatment_Code) String5    
 ,0 as Double1    
 ,min(ta.sa_transacno) as STRING8    
 ,0 as DOUBLE7    
 ,max(ta.Site_Code) as STRING9    
 ,max(ta.Site_Code) as STRING10    
 ,'' as STRING7     
 ,0 as DOUBLE2    
 ,0 as DOUBLE3    
 ,0 as DOUBLE4    
 ,0 as DOUBLE5    
 ,max(ta.treatment_parentcode) as String6    
 ,'' as DOUBLE54    
 ,0 as DOUBLE6    
 ,round(sum(ta.Amount),2) as double8    
 ,0 as double9    
 ,0 as double10    
 ,max(ta.type) as type    
 ,'' AS Package_Desc     
 ,max(ta.dt_LineNo) AS dt_LineNo    
 ,getdate() as date5    
 from Treatment_account ta    
with (nolock)     
where (ta.Type = 'DEPOSIT' OR ta.Type = 'Top Up') and  (Ta.sa_Date >= @StartDate AND Ta.sa_Date <= @EndDate) 
and ta.site_code = @siteCode    
group by ta.TREATMENT_parentCODE    
) b     
left outer join pos_haud ph on ph.sa_transacno = b.string8    
left outer join customer c on c.Cust_code = b.string3    
where b.string2 is not null    
group by b.string6    
) c    
where DOUBLE2 != Double4    
    
END 


--------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_LiabilityReport')
BEGIN
DROP PROCEDURE Web_LiabilityReport
END
GO
CREATE  PROCEDURE Web_LiabilityReport      
@FromDate Varchar(10),        
@ToDate Varchar(10),        
@Site Varchar(max),        
@Type Varchar(10),        
@CustCode Varchar(max),        
@PayMode Varchar(max),        
 @ShowZeroQty nvarchar(1)           
AS        
        
set @Site=SUBSTRING(@Site,1,4)        
set @Site=REPLACE(@Site, ',', '');        
        
Declare @FDate DATETIME        
Declare @TDate DATETIME        
Declare @T1Date DATETIME        
IF @Type='UnEarned'        
 BEGIN         
 SET @FDate=Convert(Datetime,@FromDate,103)        
 SET @TDate=Convert(Datetime,@ToDate,103)        
 SET @T1Date=Convert(Datetime,@ToDate,103)        
 END        
ELSE        
 BEGIN        
 SET @FDate=Convert(Datetime,@FromDate,103)        
 SET @TDate=Convert(Datetime,@ToDate,103)        
 SET @T1Date=Convert(Datetime,@ToDate,103)        
 SET @FDate = DATEADD(DAY,-731,@FDate)        
 SET @TDate = DATEADD(DAY,-731,@TDate)        
 END        
        
EXEC [TreatmentDetails] @FDate,@TDate,@Site,@CustCode,@PayMode        
IF OBJECT_ID('tempdb.#Data_LiabilityReport') IS NOT NULL DROP TABLE #Data_LiabilityReport        
IF OBJECT_ID('tempdb.#Data_LiabilityReportOutstanding') IS NOT NULL DROP TABLE #Data_LiabilityReportOutstanding        
        
select pos_haud.sa_transacno_ref,Treatment_Account.Outstanding  INTO #Data_LiabilityReportOutstanding         
from Treatment_Account         
inner join pos_haud on pos_haud.sa_transacno=Treatment_Account.sa_transacno        
where Treatment_Account.id in (        
select max(Treatment_Account.id) from Treatment_Account         
inner join pos_haud on pos_haud.sa_transacno=Treatment_Account.sa_transacno        
group by sa_transacno_ref)        
        
        
Select         
T1.SA_TransacNo_Ref [invoiceNum],        
T0.DATE1 [saleDate],        
T0.DATE3 [dateOfExipry],        
T0.STRING4 [customer],        
T0.STRING3 [customerRefNo],        
T2.ItemSite_Desc [outlet],        
T0.STRING2 [item],        
Case When ISNULL(T0.string31,0)=0 Then T0.DOUBLE2 Else 0 End [qty_Paid_Paid],        
Case When ISNULL(T0.string31,0)=0 Then T0.DOUBLE3 Else 0 End [qty_Paid_Used],        
Case When ISNULL(T0.string31,0)=0 Then T0.DOUBLE4 Else 0 End [qty_Paid_Refunded],        
Case When ISNULL(T0.string31,0)=0 Then T0.DOUBLE5 Else 0 End [qty_Paid_Balance],        
Case When ISNULL(T0.string31,0)=1 Then T0.DOUBLE2 Else 0 End [qty_FOC_Paid],        
Case When ISNULL(T0.string31,0)=1 Then T0.DOUBLE3 Else 0 End [qty_FOC_Used],        
Case When ISNULL(T0.string31,0)=1 Then T0.DOUBLE4 Else 0 End [qty_FOC_Refunded],        
Case When ISNULL(T0.string31,0)=1 Then T0.DOUBLE5 Else 0 End [qty_FOC_Balance],        
0 [Contra_In],        
0 [Contra_Out],        
T0.DOUBLE1*T0.DOUBLE2 [paid],        
T0.DOUBLE1*T0.DOUBLE3 [redeemed],        
T0.DOUBLE1*T0.DOUBLE5 [unEarned],        
T3.Outstanding        
INTO #Data_LiabilityReport        
 from ReportTmpMData T0         
 JOIN pos_haud T1 ON T0.STRING8=T1.sa_transacno        
 Join Item_SiteList T2 ON T2.ItemSite_Code=T0.STRING10        
 Join #Data_LiabilityReportOutstanding T3 ON T1.SA_TransacNo_Ref=T3.sa_transacno_ref        
-- Where Double1<>0       
--  And ((@ShowZeroQty='Y') OR (T0.DOUBLE1*T0.DOUBLE5)<>0)         
    Where ((@ShowZeroQty='Y') or (T0.DOUBLE1*T0.DOUBLE5) <>0)         
    
-- Update #Data_LiabilityReport Set dateOfExipry='20600101' Where dateOfExipry='19900101'        
--select * from ReportTmpMData  order by string13        
--SELECT Convert(Varchar(10),[dateOfExipry],112), * FROM #Data_LiabilityReport         
--select Convert(Varchar(10),@T1Date,112)        
--select @Type        
 IF @Type='UnEarned'        
  BEGIN        
   SELECT * FROM #Data_LiabilityReport Where Convert(Varchar(10),[dateOfExipry],112)>Convert(Varchar(10),@T1Date,112)        
 END        
 ELSE        
 BEGIN        
   --SELECT * FROM #Data_LiabilityReport Where Convert(Varchar(10),[dateOfExipry],112)<=Convert(Varchar(10),@TDate,112)        
   SELECT * FROM #Data_LiabilityReport Where Convert(Varchar(10),[dateOfExipry],112)<=Convert(Varchar(10),@T1Date,112)         
   ORDER BY  [invoiceNum]        
 END 

-----------





IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionReportGT1AndGT2')
BEGIN
DROP PROCEDURE Web_SaleCollectionReportGT1AndGT2
END
GO
create  procedure Web_SaleCollectionReportGT1AndGT2     
      
@FromDate Varchar(10),      
@ToDate Varchar(10),      
@Site Varchar(max),      
@Type Varchar(10),      
@PayMode Varchar(max)      
AS      
Declare @FDate DATETIME      
Declare @TDate DATETIME      
SET @FDate=Convert(Datetime,@FromDate,103)      
SET @TDate=Convert(Datetime,@ToDate,103)      
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport      
      
Select X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],            
X.payTypes [payTypes],      
(case when X.[isVoid]=1 then 'Voided Sales'  when X.[Group]='GT1' and X.[isVoid]=0 and isnull(SUM(X.total),0)<>0 then 'Sales' 
when ((X.[Group]='GT2' and X.[isVoid]=0) or (isnull(SUM(X.total),0)=0)) then 'Non-Sales' else '' end) as SalesGroup,      
X.ItemSite_Code [siteCode],      
X.ItemSite_Desc [siteName],      
isnull(SUM(X.amt),0) [amt],      
isnull(SUM(X.payCN),0) [payCN],      
isnull(SUM(X.payContra),0) [payContra],      
isnull(SUM(X.grossAmt),0) [grossAmt],   
isnull(SUM(X.taxes),0) [taxes],  
isnull(SUM(X.gstRate),0) [gstRate],            
isnull(SUM(X.grossAmt),0)-isnull(SUM(X.taxes),0) [netAmt],      
isnull(SUM(X.BankCharges),0) [BankCharges],      
isnull(SUM(X.comm),0) [comm],      
isnull(SUM(X.grossAmt),0)-isnull(SUM(X.taxes),0)-isnull(SUM(X.BankCharges),0) total        
from (      
SELECT              
convert (varchar,pos_haud.sa_date,103)[payDate],       
Customer.Cust_name [customer],        
pos_haud.SA_TransacNo_Ref [invoiceRef],       
pos_haud.isVoid,      
pos_haud.sa_remark,      
--pos_haud.sa_transacno [payRef],      
pos_haud.sa_staffname [payRef],      
Customer.Cust_Refer [CustRef],      
pos_taud.pay_Desc [payTypes],       
pos_taud.pay_actamt  [amt] ,       
0 [payContra],      
paytable.GT_Group [Group],      
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],      
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],      
   
 case when ((Select top 1 site_is_gst from item_sitelist where ((@Site='') OR ((@Site<>'') And item_sitelist.ItemSite_Code In 
(Select Item From dbo.LISTTABLE(@Site,',')))))=1) then  
 (case when ((paytable.GT_Group='GT2' and pos_haud.[isVoid]=0) or       
(isnull(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-       
(CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) -       
(isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else 
(pos_taud.pay_actamt/107)*7 End) )/100  +0 , 3),0)=0)) then 0 else Convert(Decimal(19,3),(pos_taud.pay_actamt/107)*7) end)  
   else  
   0   
   end     
   [taxes],  

Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then pos_taud.PAY_GST else (CASE When 
(pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) end) [gstRate],      
      
round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then 
(pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) , 3) [netAmt],      
      

      
0 [comm],      
round((isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 
Else (pos_taud.pay_actamt/107)*7 End ))/100 ,3) as [BankCharges],      
round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-(CASE When 
(pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End)  - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) )/100  +0 , 3) [total],      
pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc      
FROM pos_haud       
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno         
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code       
INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code       
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE      
Where pos_haud.sa_date>=@FDate + '00:00:00.000' And pos_haud.sa_date<=@TDate  + '23:59:59.999'    
    
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site      
And ((@PayMode='') OR ((@PayMode<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayMode,',')))) --pay      
)X      
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,[payRef],
[CustRef],X.[Group],X.isVoid,X.sa_remark 
------------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_StockBalanceReportA')
BEGIN
DROP PROCEDURE Web_StockBalanceReportA
END
GO

create procedure Web_StockBalanceReportA 
                                    
 @TDate Varchar(10),                                        
 @Site nvarchar(255),                                         
 @Dept nvarchar(255),                                        
 @Range nvarchar(255),                                         
 @Brand nvarchar(255),                                        
 @FItem nvarchar(255),                                        
 @TItem nvarchar(255),                                        
 @ShowInactive nvarchar(1),                                        
 @ShowZeroQty nvarchar(1)                                        
                                        
AS                                        
BEGIN                                        
    Select * from                       
    (                                        
    SELECT  distinct Stock.Item_Name [ItemName],Stock.ITEM_CODE [ItemCode],item_div.itm_desc [itm_desc],item_brand.itm_desc [site],
item_range.itm_desc [Product],Stktrn_2.STORE_NO [Outlet],ITEM_UOMPRICE.ITEM_UOM [UOM],ITEM_UOMPRICE.ITEM_PRICE [Cost],      
  
    
      
                             
    --ITEM_BATCH.QTY [Qty],ITEM_UOMPRICE.ITEM_PRICE * ITEM_BATCH.QTY [TAmt],                                        
 Stktrn_2.trn_balqty [Qty],ITEM_UOMPRICE.ITEM_PRICE * ITEM_BATCH.QTY [TAmt],                                        
 ---DENSE_RANK () OVER(PARTITION BY Stktrn_2.STORE_NO,Stktrn_2.ITEMCODE,ITEM_UOMPRICE.ITEM_UOM ORDER BY Stktrn_2.ID DESC  ) AS RankRank                                        
 --DENSE_RANK () OVER(PARTITION BY Stktrn_2.STORE_NO,Stktrn_2.ITEMCODE,ITEM_UOMPRICE.ITEM_UOM ORDER BY Stktrn_2.ID DESC  ) AS RankRank                                        
 --DENSE_RANK () OVER(PARTITION BY Stktrn_2.STORE_NO,Stktrn_2.ITEMCODE,ITEM_UOMPRICE.ITEM_UOM ORDER BY Stktrn_2.trn_post desc,Stktrn_2.id desc ) AS RankRank                                        
    DENSE_RANK () OVER(PARTITION BY Stktrn_2.STORE_NO,Stktrn_2.ITEMCODE,ITEM_UOMPRICE.ITEM_UOM ORDER BY Stktrn_2.trn_post desc,Stktrn_2.post_time desc, Stktrn_2.Id desc) AS RankRank                                        
    FROM item_Class INNER JOIN                                         
    Stock INNER JOIN                                         
    Item_StockList ON Stock.item_code = Item_StockList.Item_Code  INNER JOIN                                         
    Item_Div ON Stock.Item_Div = Item_Div.itm_code INNER JOIN                                         
    Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code ON item_Class.itm_code = Stock.Item_Class INNER JOIN                                         
    Item_Brand ON Stock.item_Brand = Item_Brand.itm_code LEFT OUTER JOIN                                         
    Item_Range ON Stock.Item_Range = Item_Range.itm_code RIGHT OUTER JOIN                                         
    ITEM_BATCH ON Item_StockList.ItemSite_Code = ITEM_BATCH.SITE_CODE AND Item_StockList.Item_Code = ITEM_BATCH.ITEM_CODE INNER JOIN                                         
    ITEM_UOMPRICE ON ITEM_BATCH.UOM = ITEM_UOMPRICE.ITEM_UOM AND ITEM_BATCH.ITEM_CODE = ITEM_UOMPRICE.ITEM_CODE INNER JOIN                                         
    Stktrn AS Stktrn_2 ON Stock.item_code + '0000' = Stktrn_2.ITEMCODE   RIGHT OUTER JOIN                                         
    Item_SiteList ON Stktrn_2.STORE_NO = Item_SiteList.ItemSite_Code AND ITEM_BATCH.SITE_CODE = Item_SiteList.ItemSite_Code                                          
 Where ISNULL(Stktrn_2.ITEMCODE,'')<>''                                          
 And  Stktrn_2.Trn_Post <=Convert(Date,@TDate,103) --Date                   
 And     Stktrn_2.Post_time <> ''                                 
 And ((@FItem='Select') OR Stock.item_desc >= @FItem) AND ((@TItem='Select') OR  Stock.item_desc <= @TItem) --Item                                        
 And ((@Site='') OR ((@Site<>'') And Stktrn_2.store_no In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site                                        
 And ((@Dept='') OR ((@Dept<>'')  And  item_dept.itm_code In (Select Item From dbo.LISTTABLE(@Dept,',')))) --Dept                                    
 And ((@Brand='') OR ((@Brand<>'')  And item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand     
      
 And ((@Range='') OR ((@Range<>'')  And item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range                        
                                          
 And ((@ShowInactive='Y') OR Stock.Item_Isactive =1)               
              
             
 And Stock.Item_Div Between '1' And  '2'  And Item_SiteList.ItemSite_Isactive = 'True'                                        
 And ITEM_UOMPRICE.IsActive = 'True'                                      
 )X Where X.RankRank=1                                               
    
 And ((@ShowZeroQty='Y') OR X.Qty<>0)                     
       order by  [Product],[ITEMNAME]                                  
                                        
END                                         
-------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_StockMovementDetailReport')
BEGIN
DROP PROCEDURE Web_StockMovementDetailReport
END
GO
create procedure Web_StockMovementDetailReport 
                            
 @FromDate Varchar(10),                                  
 @ToDate nvarchar(10),                                    
 @Site nvarchar(255),                                  
 @Dept nvarchar(255),                                  
 @Range nvarchar(255),                                   
 @Brand nvarchar(255),                                   
 @FItem nvarchar(255),                                  
 @TItem nvarchar(255),                                   
 @MovementCode nvarchar(255),                                  
 @MovementType nvarchar(255),                                  
 @Supplier nvarchar(255)                                  
AS               
    Declare @FDate DATETIME                      
Declare @TDate DATETIME                      
SET @FDate=Convert(Date,@FromDate,103)                      
SET @TDate=Convert(Date,@ToDate,103)                             
BEGIN                                  
SELECT       
Stktrn.Store_No [Store],      
Stktrn.ITEMCODE [ItemCode],      
ISNULL(MATRIX.ITEM_NAME,'') [ItemName],      
ISNULL(Stktrn.Item_UOM,'') [ItemUOM],      
ISNULL(ITEM_RANGE.ITM_DESC,'') [ItemRange],      
---ISNULL(pos_haud.SA_TransacNo_Ref,'') [TranNo],      
---ISNULL(Stktrn.TRN_DOCNO,'') [TranNo],      
(case when Stktrn.TRN_TYPE='SA' then (select top 1 sa_transacno_ref from pos_haud where sa_transacno=Stktrn.TRN_DOCNO)           
when Stktrn.TRN_TYPE='VT' then (select top 1 sa_transacno_ref from pos_haud where sa_transacno=Stktrn.TRN_DOCNO)            
else ISNULL(Stktrn.TRN_DOCNO,'') END) as [TranNo],           
--Stktrn.TRN_POST [PostDate],      
--Stktrn.TRN_DATE [TranDate],      
isnull(Stktrn.POST_TIME,'') [PostTime],      
isnull(Stktrn.ID,'') [ID],      
isnull(Convert(Date,Stktrn.TRN_POST,103),'') [PostDate],      
isnull(Convert(Date,Stktrn.TRN_DATE,103),'') [TranDate],      
Stktrn.TRN_TYPE [TranType],      
ISNULL(pos_haud.sa_custname,'') [Customer],      
ISNULL(Stktrn.FSTORE_NO,'') [FromStore],      
ISNULL(Stktrn.TSTORE_NO,'') [ToStore],      
Stktrn.TRN_QTY [TranQty],      
(case when Stktrn.TRN_TYPE='SA' then Stktrn.TRN_QTY else 0 end) as [TranQtySA],      
ISNULL(Stktrn.TRN_AMT,0) [TranAmt],      
Stktrn.TRN_BALQTY [Balance],      
Item_SiteList.ItemSite_Desc [Outlet],      
isnull(ITEM_SUPPLY.SUPPLYDESC,'') [Supplier],         
isnull(Stk_MovDoc_Hdr.DOC_REMK1,'') [Remarks]      
FROM Item_Div INNER JOIN Stktrn INNER JOIN MATRIX ON Stktrn.ITEMCODE = MATRIX.ITEM_BARCODE       
LEFT OUTER JOIN Stk_MovDoc_Hdr on  Stktrn.TRN_DOCNO=Stk_MovDoc_Hdr.DOC_NO        
--INNER JOIN Stk_MovDoc_Hdr on  TranNo=Stk_MovDoc_Hdr.DOC_NO        
inner join   Stock LEFT OUTER JOIN ITEM_RANGE ON ITEM_RANGE.ITM_CODE = STOCK.ITEM_RANGE ON MATRIX.ITEM_CODE = Stock.item_code       
INNER JOIN Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code ON Item_Div.itm_code = Stock.Item_Div INNER JOIN item_Class ON Stock.Item_Class = item_Class.itm_code       
INNER JOIN ITEM_UOMPRICE ON Stktrn.Item_UOM = ITEM_UOMPRICE.ITEM_UOM AND Stktrn.ITEMCODE = ITEM_UOMPRICE.ITEM_CODE + '0000'       
INNER JOIN Item_Brand ON Stock.item_Brand = Item_Brand.itm_code INNER JOIN Item_SiteList ON Stktrn.STORE_NO = Item_SiteList.ItemSite_Code       
LEFT OUTER JOIN pos_haud ON Stktrn.TRN_DOCNO = pos_haud.sa_transacno         
LEFT OUTER JOIN ITEM_SUPPLY ON STOCK.ITEM_SUPP = ITEM_SUPPLY.SPLY_CODE    WHERE                                     
--stktrn.Trn_Post >=Convert(Date,@FromDate,103) And stktrn.Trn_Post <=Convert(Date,@ToDate,103) --Date                                     
--stktrn.Trn_Date >=Convert(Date,@FromDate,103) And stktrn.Trn_Date <=Convert(Date,@ToDate,103) --Date            
---   Stktrn.TRN_DOCNO=Stk_MovDoc_Hdr.DOC_NO                           
(stktrn.Trn_Date between @FDate And @TDate) --Date                                    
And (stktrn.Trn_Post between @FDate And @TDate) --Date              
And ((@FItem='Select') OR Stock.item_desc >= @FItem) AND ((@TItem='Select') OR  Stock.item_desc <= @TItem) --Item                                    
And ((@Site='') OR ((@Site<>'') And stktrn.store_no In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site                                    
And ((@Dept='') OR ((@Dept<>'') And item_dept.itm_code In (Select Item From dbo.LISTTABLE(@Dept,',')))) --Dept           
And ((@Brand='') OR ((@Brand<>'') And item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand                                    
And ((@Range='') OR ((@Range<>'') And item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range                                    
And ((@MovementCode='') OR ((@MovementCode<>'') And Stktrn.TRN_TYPE In (Select Item From dbo.LISTTABLE(@MovementCode,','))))  --Movement Code                                    
                                    
And ((@MovementType='All') OR (@MovementType='In' And Stktrn.TRN_QTY > 0) OR (@MovementType='Out' And Stktrn.TRN_QTY < 0)) --Movement Type                      
And ((@Supplier='') OR ((@Supplier<>'') And STOCK.ITEM_SUPP In (Select Item From dbo.LISTTABLE(@Supplier,','))))  --Supplier                                
    Order by Stktrn.ITEMCODE,Stktrn.TRN_POST,Stktrn.Post_Time,Stktrn.id                            
END
-------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_StockMovementSummaryReport')
BEGIN
DROP PROCEDURE Web_StockMovementSummaryReport
END
GO
CREATE   PROCEDURE Web_StockMovementSummaryReport                    
 @Mon int,                        
 @Yr int,                        
 @Site nvarchar(Max),                                     
 @Dept nvarchar(Max),                        
 @Range nvarchar(Max),                        
 @Brand nvarchar(Max),                         
 @FItem nvarchar(Max),                        
 @TItem nvarchar(Max),                        
 @MovementCode nvarchar(Max)    
AS                        
                        
 DECLARE @COLS AS NVARCHAR(MAX),                        
    @COLS_SUM  AS NVARCHAR(MAX),                        
    @COLS_SUM_IN  AS NVARCHAR(MAX),                        
    @COLS_SUM_OUT  AS NVARCHAR(MAX),                        
 @COLS_SUM_TOTAL  AS NVARCHAR(MAX),                        
 @QUERY AS NVARCHAR(MAX)                        
SELECT @COLS = STUFF((                        
            Select ',' +'['+[Col]+']' from                        
   (SELECT DISTINCT Convert(Varchar(2),number)+'In' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31                        
   UNION                        
   SELECT DISTINCT Convert(Varchar(2),number)+'Out' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31)X Order By X.number                        
            FOR XML PATH(''), TYPE                        
            ).value('.', 'NVARCHAR(MAX)')                         
        ,1,1,'')                        
SELECT @COLS_SUM = STUFF((                        
            Select ',' +'SUM(ISNULL(['+[Col]+'],0)) As ['+[Col]+']' from                        
   (SELECT DISTINCT Convert(Varchar(2),number)+'In' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31                        
   UNION                        
   SELECT DISTINCT Convert(Varchar(2),number)+'Out' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31)X Order By X.number                        
            FOR XML PATH(''), TYPE                        
            ).value('.', 'NVARCHAR(MAX)')                         
        ,1,1,'')                        
SELECT @COLS_SUM_IN = STUFF((                        
            Select '+' +'SUM(ISNULL(['+[Col]+'],0))' from                        
   (SELECT DISTINCT Convert(Varchar(2),number)+'In' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31                        
   )X Order By X.number                        
            FOR XML PATH(''), TYPE                        
            ).value('.', 'NVARCHAR(MAX)')                         
        ,1,1,'')                        
SELECT @COLS_SUM_OUT = STUFF((                        
            Select '+' +'SUM(ISNULL(['+[Col]+'],0))' from                        
   (                        
   SELECT DISTINCT Convert(Varchar(2),number)+'Out' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31)X Order By X.number                        
            FOR XML PATH(''), TYPE                        
            ).value('.', 'NVARCHAR(MAX)')                         
        ,1,1,'')                        
SELECT @COLS_SUM_TOTAL = STUFF((                        
            Select '+' +'SUM(ISNULL(['+[Col]+'],0))' from                        
   (SELECT DISTINCT Convert(Varchar(2),number)+'In' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31                        
   UNION                        
   SELECT DISTINCT Convert(Varchar(2),number)+'Out' [Col],number                        
   FROM master..spt_values                        
   WHERE number BETWEEN 1 AND 31)X Order By X.number                        
            FOR XML PATH(''), TYPE                        
            ).value('.', 'NVARCHAR(MAX)')                         
        ,1,1,'')                        
                 
--UPDATE STKTRN SET STOCK_IN = 1 WHERE MONTH(STKTRN.TRN_POST)=@Mon AND YEAR(STKTRN.TRN_POST)=@Yr AND STORE_NO=@Site AND  STKTRN.TRN_QTY >= 0                         
--UPDATE STKTRN SET STOCK_IN = 0 WHERE MONTH(STKTRN.TRN_POST)=@Mon AND YEAR(STKTRN.TRN_POST)=@Yr AND STORE_NO=@Site AND  STKTRN.TRN_QTY < 0              
UPDATE STKTRN SET STOCK_IN = 1 WHERE MONTH(STKTRN.TRN_POST)=@Mon AND YEAR(STKTRN.TRN_POST)=@Yr AND STORE_NO In (Select Item From dbo.LISTTABLE(@Site,',')) AND 
 STKTRN.TRN_QTY >= 0                         
UPDATE STKTRN SET STOCK_IN = 0 WHERE MONTH(STKTRN.TRN_POST)=@Mon AND YEAR(STKTRN.TRN_POST)=@Yr AND STORE_NO In (Select Item From dbo.LISTTABLE(@Site,',')) AND  
STKTRN.TRN_QTY < 0              
       
 ---STORE_NO In (Select Item From dbo.LISTTABLE(@Site,','))         
                            
SELECT Stktrn.ITEMCODE [ItemCode],                                            
--Stock.Item_Desc + ' (' + isnull(Stock.item_uom,'') + ')'  as [ItemName],                         
Stock.Item_Desc  [ItemName],                         

(Select TOP 1 TRN_BALQTY-TRN_QTY  from Stktrn X Where X.ITEMCODE=Stktrn.ITEMCODE AND MONTH( X.TRN_POST)=@Mon 
AND YEAR( X.TRN_POST)=@Yr AND  X.STORE_NO In (Select Item From dbo.LISTTABLE(@Site,','))   Order By trn_post ASC,id ASC) [Open],                  
  
      
(Select TOP 1 TRN_BALQTY  from Stktrn X Where X.ITEMCODE=Stktrn.ITEMCODE AND MONTH( X.TRN_POST)=@Mon 
AND YEAR( X.TRN_POST)=@Yr AND  X.STORE_NO In (Select Item From dbo.LISTTABLE(@Site,','))   Order By trn_post desc,id desc) [Close],                       
 
      
SUM(TRN_QTY) AS TrnQty,                        
      
Case When Stock_In=1 Then Convert(Varchar(2),DAY(TRN_POST))+'In' Else Convert(Varchar(2),DAY(TRN_POST))+'Out' End [Direction]                        

INTO ##TEMP_1                        
FROM Stktrn  INNER JOIN Stock ON ITEMCODE = Stock.item_code + '0000'                     
INNER JOIN Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code  INNER JOIN item_Range ON Stock.Item_Range = item_Range.itm_code  
INNER JOIN Item_Brand ON Stock.item_Brand = Item_Brand.itm_code                        
            
WHERE  MONTH(Stktrn.TRN_POST)=@Mon AND YEAR(Stktrn.TRN_POST)=@Yr AND                    
--WHERE  MONTH(T0.TRN_DATE)=@Mon AND YEAR(T0.TRN_DATE)=@Yr AND                    
(Stock.Item_Div = 1 or Stock.Item_Div = 2 ) AND          
--- STORE_NO=@Site                       
 STORE_NO In (Select Item From dbo.LISTTABLE(@Site,','))        
And ((@FItem='Select') OR Stock.item_desc >= @FItem) AND ((@TItem='Select') OR  Stock.item_desc <= @TItem) --Item                        
And ((@Dept='') OR ((@Dept<>'') And Item_Dept.itm_code In (Select Item From dbo.LISTTABLE(@Dept,',')))) --Dept                        
And ((@Brand='') OR ((@Brand<>'') And Item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand                        
And ((@Range='') OR ((@Range<>'') And Item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range                        
And ((@MovementCode='') OR ((@MovementCode<>'') And Stktrn.TRN_TYPE In (Select Item From dbo.LISTTABLE(@MovementCode,','))))  --Movement Code                                        
    
Group By Stock.Item_Desc,ITEMCODE,DAY(TRN_POST),Stock_In                     
--Group By ITEMCODE,Stock.Item_Desc,DAY(TRN_DATE),Stock_In                     
---order by ITEMCODE desc            
                        
SET @QUERY = 'SELECT ItemName,ItemCode,[Open],' + @COLS_SUM + ',' + @COLS_SUM_IN + ' [TotalIn],' + @COLS_SUM_OUT + ' [TotalOut],' + @COLS_SUM_TOTAL + ' [Total],[Close] from         
             (                        
                SELECT * FROM ##TEMP_1              
            )  X                             
            PIVOT                  
            (                       
                SUM(TrnQty)                        
                FOR Direction IN (' + @COLS + ')                       
            )  p  GROUP BY ItemName,ItemCode,[Open],[Close] '                        
                        
EXECUTE(@QUERY);                        
---PRINT(@QUERY);                        
                        
DROP TABLE ##TEMP_1 
----------  
----------

----
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionReportA')
BEGIN
DROP PROCEDURE Web_DailyCollectionReportA
END
GO
create    procedure Web_DailyCollectionReportA   
                                 
 @FromDate Varchar(10),                                    
 @ToDate Varchar(10),                                    
  @FSite nvarchar(Max),                                  
  @TSite nvarchar(Max)                                   
AS                                    
Declare @FDate Datetime                                
Declare @TDate Datetime                                
SET @FDate=Convert(Date,@FromDate,103)                                    
SET @TDate=Convert(Date,@ToDate,103)      
select  CONVERT(date,sa_date,103) as [sa_date],  
(case when sum(Pay_actamt)=0 then isnull(sum(SrvSales_Deposit),0) else (isnull(sum(SrvSales_Deposit),0) * (isnull(sum(GT1_ActAmt),0)/isnull(sum(Pay_actamt),1))) end) as [svcsales],    
 (case when sum(Pay_actamt)=0 then 0 else (isnull(sum(SrvSales_Deposit),0) * (isnull(sum(GT2_ActAmt),0)/isnull(sum(Pay_actamt),1))) end) as [svcnonsales],    
 (case when sum(Pay_actamt)=0 then isnull(sum(ProSales_Deposita),0) else (isnull(sum(ProSales_Deposita),0) * (isnull(sum(GT1_ActAmt),0)/isnull(sum(Pay_actamt),1))) end) as [prdsales],    
 (case when sum(Pay_actamt)=0 then 0 else (isnull(sum(ProSales_Deposita),0) * (isnull(sum(GT2_ActAmt),0)/isnull(sum(Pay_actamt),1))) end) as [prdnonsales]
 from  
(SELECT pos_haud.itemsite_code,  pos_haud.sa_date,  pos_haud.sa_transacno, SrvSales.SrvSales_Deposit, ProSales.ProSales_Deposita, 
GT1_actamt.GT1_actamt, GT2_actamt.GT2_actamt, Pay_actamt.Pay_actamt  
FROM         pos_haud LEFT OUTER JOIN  
  
(SELECT     pos_taud_1.sa_transacno, SUM(pos_taud_1.pay_actamt) AS GT2_actamt  
FROM          pos_taud AS pos_taud_1 INNER JOIN  
PAYTABLE AS PAYTABLE_1 ON pos_taud_1.pay_type = PAYTABLE_1.pay_code  
WHERE      (PAYTABLE_1.GT_Group = 'GT2')  
GROUP BY pos_taud_1.sa_transacno) AS GT2_actamt ON pos_haud.sa_transacno = GT2_actamt.sa_transacno LEFT OUTER JOIN  
(SELECT     pos_taud.sa_transacno, SUM(pos_taud.pay_actamt) AS GT1_actamt  
FROM          pos_taud INNER JOIN  
PAYTABLE ON pos_taud.pay_type = PAYTABLE.pay_code  
WHERE      (PAYTABLE.GT_Group = 'GT1')  
GROUP BY pos_taud.sa_transacno) AS GT1_actamt ON pos_haud.sa_transacno = GT1_actamt.sa_transacno LEFT OUTER JOIN  
(SELECT     sa_transacno, SUM(pay_actamt) AS Pay_actamt  
FROM          pos_taud AS pos_taud_2  
GROUP BY sa_transacno) AS Pay_actamt ON pos_haud.sa_transacno = Pay_actamt.sa_transacno LEFT OUTER JOIN  
(SELECT     sa_transacno, SUM(dt_deposit) AS SrvSales_Deposit  
FROM          pos_daud  
WHERE      (Record_Detail_Type IN ('SERVICE', 'TP SERVICE', 'PACKAGE', 'TP PACKAGE'))  
GROUP BY sa_transacno) AS SrvSales ON pos_haud.sa_transacno = SrvSales.sa_transacno LEFT OUTER JOIN  
(SELECT     sa_transacno, SUM(dt_deposit) AS ProSales_Deposita  
FROM          pos_daud AS pos_daud_1  
WHERE      (Record_Detail_Type IN ('PRODUCT', 'TP PRODUCT'))  
GROUP BY sa_transacno) AS ProSales ON pos_haud.sa_transacno = ProSales.sa_transacno  
where pos_haud.isvoid = 0) as Sales_Record  
WHERE     (sa_date >= @FDate + ' 00:00:00.000' and sa_date <= @TDate + ' 23:59:59.999')  
and itemsite_code>=@FSite and itemsite_code<=@TSite  
-- and Pay_actamt <> 0  
group by sa_date order by sa_date  

--------

-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionReportA1')
BEGIN
DROP PROCEDURE Web_DailyCollectionReportA1
END
GO  
CREATE    PROCEDURE Web_DailyCollectionReportA1                                  
 @FromDate Varchar(10),                                  
 @ToDate Varchar(10),                                  
  @FSite nvarchar(Max),                                
  @TSite nvarchar(Max)                                 
AS                                  
Declare @FDate Datetime                               
Declare @TDate Datetime                              
SET @FDate=Convert(Datetime,@FromDate + ' 00:00:00.000',103)                                  
SET @TDate=Convert(Datetime,@ToDate + ' 23:59:59.000',103)                                  
                                
select  CONVERT(date,pos_haud.sa_date,103) as [sa_date],                              
(select ISNULL(sum(proportions),0) from (select distinct ph.sa_status, pd.dt_status, ph.sa_custno,                             
ph.sa_custname, ph.sa_date, pt.dt_LineNo AS Pay_LineNo, pt.pay_group, ptb.bank_charges, ptb.gt_group,                             
il.itemsite_code, il.itemsite_desc, ph.sa_transacno_ref, pd.sa_transacno, pd.dt_itemdesc,                             
pd.dt_deposit, pd.dt_price, pd.gst_amt_collect, pt.pay_type, pt.pay_desc, pt.pay_tendamt,                             
(select sum(dt_qty) from pos_daud where   sa_transacno = ph.sa_transacno and dt_itemno = pd.dt_itemno                             
and dt_lineno = pd.dt_lineno group by dt_itemno, sa_transacno) as dt_qty,                             
(select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno and                             
pos_taud.pay_type = pt.pay_type GROUP by sa_transacno) as sumpayments, isnull((select sum(dt_deposit)                             
from pos_daud where  sa_transacno = pd.sa_transacno and dt_itemno = pd.dt_itemno and dt_lineno = pd.dt_lineno and                             
dt_itemdesc + ' ' + convert(nvarchar, dt_deposit) = pd.dt_itemdesc + ' ' +                             
convert(nvarchar,pd.dt_deposit)  and pd.record_detail_type<> 'TD'   and                                 
right(pd.dt_itemdesc,5) <> '(FOC)') * ((pt.pay_tendamt) / (select sum(pay_tendamt) from pos_taud                             
where sa_transacno = pt.sa_transacno and pay_tendamt<> 0 GROUP by sa_transacno)),0) as proportions,                             
(pt.pay_tendamt / case (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno                             
GROUP by sa_transacno) when 0 then 1 else (select sum(pay_tendamt) from pos_taud where                             
sa_transacno = pt.sa_transacno) end ) * ((gst_amt_collect)) as gst_proportions from pos_daud pd                             
inner join pos_taud pt on pt.sa_transacno = pd.sa_transacno inner join pos_haud ph on                             
ph.sa_transacno = pd.sa_transacno and ph.IsVoid=0 inner join item_sitelist il on il.itemsite_code = ph.itemsite_code                             
inner join paytable ptb on ptb.pay_code = pt.pay_type where pd.record_detail_type IN                             
('SERVICE', 'TP SERVICE', 'PACKAGE', 'TP PACKAGE') and ptb.gt_group = 'GT1' and                             
ph.sa_date = pos_haud.sa_date) as prd) as svcsales ,                                 
                                
(select ISNULL(sum(proportions),0) from (select distinct ph.sa_status, pd.dt_status, ph.sa_custno,                             
ph.sa_custname, ph.sa_date, pt.dt_LineNo AS Pay_LineNo, pt.pay_group, ptb.bank_charges, ptb.gt_group,                            
 il.itemsite_code, il.itemsite_desc, ph.sa_transacno_ref, pd.sa_transacno, pd.dt_itemdesc,                             
 pd.dt_deposit, pd.dt_price, pd.gst_amt_collect, pt.pay_type, pt.pay_desc, pt.pay_tendamt,                             
 (select sum(dt_qty) from pos_daud where sa_transacno = ph.sa_transacno and dt_itemno = pd.dt_itemno                             
 and dt_lineno = pd.dt_lineno group by dt_itemno, sa_transacno) as dt_qty, (select sum(pay_tendamt)                            
  from pos_taud where sa_transacno = pt.sa_transacno and pos_taud.pay_type = pt.pay_type GROUP by                             
  sa_transacno) as sumpayments, isnull((select sum(dt_deposit) from pos_daud where                            
   sa_transacno = pd.sa_transacno and dt_itemno = pd.dt_itemno and dt_lineno = pd.dt_lineno and                             
   dt_itemdesc + ' ' + convert(nvarchar, dt_deposit) = pd.dt_itemdesc + ' ' +                             
   convert(nvarchar,pd.dt_deposit)  and pd.record_detail_type<> 'TD' and                               
   right(pd.dt_itemdesc,5) <> '(FOC)') * ((pt.pay_tendamt) / (select sum(pay_tendamt) from pos_taud                             
   where sa_transacno = pt.sa_transacno and pay_tendamt<> 0 GROUP by sa_transacno)),0) as proportions,                             
   (pt.pay_tendamt / case (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno                             
   GROUP by sa_transacno) when 0 then 1 else (select sum(pay_tendamt) from pos_taud where sa_transacno                             
   = pt.sa_transacno) end ) * ((gst_amt_collect)) as gst_proportions from pos_daud pd inner join                            
    pos_taud pt on pt.sa_transacno = pd.sa_transacno inner join pos_haud ph on ph.sa_transacno =                            
     pd.sa_transacno inner join                             
item_sitelist il on il.itemsite_code = ph.itemsite_code inner join paytable ptb on ptb.pay_code =                             
pt.pay_type where pd.record_detail_type IN ('SERVICE', 'TP SERVICE', 'PACKAGE', 'TP PACKAGE')                             
and ptb.gt_group = 'GT2' and pt.pay_Type= 'OB' and ph.sa_date = pos_haud.sa_date) as prd) as svcnonsales ,                                 
                                 
 (select ISNULL(sum(proportions),0) from (select distinct ph.sa_status, pd.dt_status, ph.sa_custno, ph.sa_custname,                             
 ph.sa_date, pt.dt_LineNo AS Pay_LineNo, pt.pay_group, ptb.bank_charges, ptb.gt_group, il.itemsite_code, il.itemsite_desc,                             
 ph.sa_transacno_ref, pd.sa_transacno, pd.dt_itemdesc, pd.dt_deposit, pd.dt_price,pd.gst_amt_collect, pt.pay_type,                             
pt.pay_desc, pt.pay_tendamt, (select sum(dt_qty) from pos_daud where sa_transacno = ph.sa_transacno                             
and dt_itemno = pd.dt_itemno and dt_lineno = pd.dt_lineno group by dt_itemno, sa_transacno) as dt_qty,                             
(select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno and                             
pos_taud.pay_type = pt.pay_type GROUP by sa_transacno) as sumpayments, isnull((select sum(dt_deposit)                            
 from pos_daud where sa_transacno = pd.sa_transacno and dt_itemno = pd.dt_itemno  and dt_lineno = pd.dt_lineno                           
 and dt_itemdesc + ' ' + convert(nvarchar, dt_deposit) = pd.dt_itemdesc + ' ' +                             
 convert(nvarchar,pd.dt_deposit)  and pd.record_detail_type<> 'TD'                             
 and right(pd.dt_itemdesc,5) <> '(FOC)') * ((pt.pay_tendamt) / (select sum(pay_tendamt) from pos_taud                             
 where sa_transacno = pt.sa_transacno and pay_tendamt<> 0 GROUP by sa_transacno)),0) as proportions,                             
 (pt.pay_tendamt / case (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno                             
 GROUP by sa_transacno) when 0 then 1 else (select sum(pay_tendamt) from pos_taud                               
 where sa_transacno = pt.sa_transacno) end ) * ((gst_amt_collect)) as gst_proportions from                             
 pos_daud pd inner join pos_taud pt on pt.sa_transacno = pd.sa_transacno  inner join pos_haud ph                             
 on ph.sa_transacno = pd.sa_transacno inner join item_sitelist il on il.itemsite_code = ph.itemsite_code        
 inner join paytable ptb on ptb.pay_code = pt.pay_type where pd.record_detail_type                             
 IN ('PRODUCT', 'TP PRODUCT') and ptb.gt_group = 'GT1' and  ph.sa_date = pos_haud.sa_date) as prd) as prdsales ,                         
                                 
 (select ISNULL(sum(proportions),0) from (select distinct ph.sa_status, pd.dt_status, ph.sa_custno,                             
 ph.sa_custname, ph.sa_date, pt.dt_LineNo AS Pay_LineNo, pt.pay_group, ptb.bank_charges, ptb.gt_group,                             
 il.itemsite_code, il.itemsite_desc, ph.sa_transacno_ref, pd.sa_transacno, pd.dt_itemdesc,                             
 pd.dt_deposit, pd.dt_price, pd.gst_amt_collect, pt.pay_type, pt.pay_desc, pt.pay_tendamt,                             
 (select sum(dt_qty) from pos_daud where sa_transacno = ph.sa_transacno and dt_itemno = pd.dt_itemno                             
 and dt_lineno = pd.dt_lineno group by dt_itemno, sa_transacno)  as dt_qty,                             
 (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno and pos_taud.pay_type =                             
 pt.pay_type GROUP by sa_transacno) as sumpayments, isnull((select sum(dt_deposit) from pos_daud                             
 where sa_transacno = pd.sa_transacno and dt_itemno = pd.dt_itemno  and dt_lineno = pd.dt_lineno and dt_itemdesc + ' ' +                             
 convert(nvarchar, dt_deposit) = pd.dt_itemdesc + ' ' + convert(nvarchar,pd.dt_deposit) and                             
 pd.record_detail_type<> 'TD' and right(pd.dt_itemdesc,5) <> '(FOC)') *                             
 ((pt.pay_tendamt) / (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno                             
 and pay_tendamt<> 0 GROUP by sa_transacno)),0) as proportions, (pt.pay_tendamt / case                             
 (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno GROUP by sa_transacno)                             
 when 0 then 1 else (select sum(pay_tendamt) from pos_taud where sa_transacno = pt.sa_transacno) end )                             
 * ((gst_amt_collect)) as gst_proportions from pos_daud pd inner join pos_taud pt on pt.sa_transacno =                             
 pd.sa_transacno inner join pos_haud ph on ph.sa_transacno = pd.sa_transacno                              
 inner join item_sitelist il on il.itemsite_code = ph.itemsite_code inner join paytable ptb on                             
 ptb.pay_code = pt.pay_type where pd.record_detail_type IN ('PRODUCT', 'TP PRODUCT') and                             
 ptb.gt_group ='GT2' and pt.pay_Type= 'OB' and ph.sa_date = pos_haud.sa_date) as prd) as prdnonsales                            
                             
  From pos_haud                                  
  where (pos_haud.sa_date >= @FDate  and pos_haud.sa_date <=@TDate )                                  
 ----where (pos_haud.sa_date between @FDate and @TDate)                                  
 ---where (pos_haud.sa_date between '2020-11-01' and '2021-02-06')                                  
 AND (pos_haud.ItemSite_Code>= @FSite AND pos_haud.ItemSite_Code<= @TSite)      
 --and  pos_haud.IsVoid = 1                              
 ---AND (pos_haud.ItemSite_Code>= 'HQ' AND pos_haud.ItemSite_Code<= 'HQ')   

-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_TopSalesPrepaidReport1')
BEGIN
DROP PROCEDURE Web_TopSalesPrepaidReport1
END
GO 
CREATE PROCEDURE Web_TopSalesPrepaidReport1
 @FromDate nvarchar(10),    
 @ToDate nvarchar(10),    
 @Site nvarchar(Max),    
 @ShowFOC  nvarchar(1),    
 @SortBy  nvarchar(10)     
     
AS    
    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate,103)    
SET @TDate=Convert(Datetime,@ToDate,103)    
  
IF @SortBy='Amount'    
BEGIN   
  
  
SELECT   
pos_haud.ItemSite_Code ,    
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,   
pos_daud.dt_qty [Qty],     
pos_daud.dt_price * pos_daud.dt_qty [amount],    
pos_daud.dt_deposit+ISNULL(T0.Deposit,0) [Paid],    
(pos_daud.dt_price * pos_daud.dt_qty)-(pos_daud.dt_deposit+ISNULL(T0.Deposit,0)) [Outstanding]  ,  
Customer.Cust_name AS Cust_Name, Item_SiteList.ItemSite_Desc AS Site_Desc, pos_haud.mac_code, pos_haud.cas_name, pos_haud.cas_logno,  
pos_haud.sa_transacno, pos_haud.sa_date, pos_haud.sa_time, pos_haud.sa_postdate, pos_haud.sa_status, pos_haud.sa_remark, pos_haud.sa_totamt,  
pos_haud.sa_totQty, pos_haud.sa_totdisc, pos_haud.sa_totgst, pos_haud.sa_totservice, pos_haud.sa_amtret, pos_haud.sa_staffno, pos_haud.sa_staffname,  
pos_haud.sa_custno, pos_haud.sa_custname, pos_haud.sa_Reason, pos_haud.sa_DiscUser, pos_haud.sa_discno, pos_haud.sa_discdesc, pos_haud.sa_discvalue,  
pos_haud.sa_discamt, pos_haud.sa_discTotal, pos_haud.ItemSite_Code, pos_haud.sa_CardNo, pos_haud.Seat_No, pos_haud.sa_depositAmt,  
pos_haud.sa_chargeAmt, pos_haud.IsVoid, pos_haud.Void_RefNo, pos_haud.Payment_Remarks, pos_haud.Next_Payment, pos_haud.Next_Appt,  
pos_haud.sa_TransacAmt, pos_haud.Appt_Time, pos_haud.Hold_Item, pos_haud.sa_discECard, pos_haud.HoldItemQty, pos_haud.WalkIn, pos_haud.Cust_Sig,  
pos_haud.sa_Round, pos_haud.Balance_Point, pos_haud.Total_Outstanding, pos_haud.Total_ItemHold_Qty, pos_haud.Total_Prepaid_Amt,  
pos_haud.Total_Voucher_Avalable, pos_haud.Total_Course_Summary, pos_haud.Total_CN_Amt, pos_haud.Previous_pts, pos_haud.Today_pts,  
pos_haud.Total_Balance_pts, pos_haud.Trans_User_Login, pos_haud.ID,   
pos_haud.SA_TransacNo_Ref, pos_haud.SA_TransacNo_Type, pos_haud.Cust_Sig_Path, pos_haud.Trans_Reason, pos_haud.Trans_Remark,  
pos_haud.Trans_RW_Point_Ratio, pos_haud.SA_Trans_DO_No, pos_haud.SA_TransacNo_Title,   
pos_haud.IssuesTrans_User_Login, pos_haud.Trans_PackageCode, pos_haud.Trans_Value, pos_haud.Trans_Pay, pos_haud.Trans_Outstanding,  
pos_haud.Used_pts, pos_haud.Earn_pts, pos_haud.Expire_Soon_Date_1, pos_haud.Expire_Soon_Point_1, pos_haud.Expire_Soon_Date_2,  
pos_haud.Expire_Soon_Point_2, pos_haud.Expire_Soon_Date_3, pos_haud.Expire_Soon_Point_3, pos_haud.Expire_Soon_Date_4, pos_haud.Expire_Soon_Point_4,  
pos_haud.Expire_Soon_Date_5, pos_haud.Expire_Soon_Point_5, pos_haud.Expire_Soon_Remark, pos_haud.Expire_Soon_Remark_Point,   
pos_taud.pay_amt, PAYTABLE.GT_Group, Customer_Class.Class_Code AS ClassCode, Customer_Class.Class_Desc AS ClassDesc, Prepaid_Account.PP_AMT,  
Prepaid_Account.Line_No, Prepaid_Account.TopUp_AMT, Prepaid_Account.TopUp_No, Prepaid_Account.ITEM_NO  
FROM Customer_Class RIGHT OUTER JOIN  
pos_haud INNER JOIN  
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno   
INNER JOIN    
pos_daud ON pos_haud.sa_transacno = pos_daud.sa_transacno    
LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit] FROM         
pos_daud INNER JOIN   
 
 Deposit_Account ON pos_daud.sa_transacno = Deposit_Account.sa_transacno   
 
  Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno And     
T0.dt_LineNo=pos_daud.dt_LineNo   
INNER JOIN  
Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code INNER JOIN  
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN  
PAYTABLE ON pos_taud.pay_type = PAYTABLE.pay_code LEFT OUTER JOIN  
Prepaid_Account ON pos_haud.sa_transacno = Prepaid_Account.PP_NO ON Customer_Class.Class_Code = Customer.Cust_Class  
where pos_daud.Record_Detail_Type = 'TP PREPAID'  
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate     
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))    
order by [amount]  
end  
ELSE  
BEGIN  
  
  
SELECT   
pos_haud.ItemSite_Code ,    
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,   
pos_daud.dt_qty [Qty],     
pos_daud.dt_price * pos_daud.dt_qty [amount],    
pos_daud.dt_deposit+ISNULL(T0.Deposit,0) [Paid],    
(pos_daud.dt_price * pos_daud.dt_qty)-(pos_daud.dt_deposit+ISNULL(T0.Deposit,0)) [Outstanding]  ,  
Customer.Cust_name AS Cust_Name, Item_SiteList.ItemSite_Desc AS Site_Desc, pos_haud.mac_code, pos_haud.cas_name, pos_haud.cas_logno,  
pos_haud.sa_transacno, pos_haud.sa_date, pos_haud.sa_time, pos_haud.sa_postdate, pos_haud.sa_status, pos_haud.sa_remark, pos_haud.sa_totamt,  
pos_haud.sa_totQty, pos_haud.sa_totdisc, pos_haud.sa_totgst, pos_haud.sa_totservice, pos_haud.sa_amtret, pos_haud.sa_staffno, pos_haud.sa_staffname,  
pos_haud.sa_custno, pos_haud.sa_custname, pos_haud.sa_Reason, pos_haud.sa_DiscUser, pos_haud.sa_discno, pos_haud.sa_discdesc, pos_haud.sa_discvalue,  
pos_haud.sa_discamt, pos_haud.sa_discTotal, pos_haud.ItemSite_Code, pos_haud.sa_CardNo, pos_haud.Seat_No, pos_haud.sa_depositAmt,  
pos_haud.sa_chargeAmt, pos_haud.IsVoid, pos_haud.Void_RefNo, pos_haud.Payment_Remarks, pos_haud.Next_Payment, pos_haud.Next_Appt,  
pos_haud.sa_TransacAmt, pos_haud.Appt_Time, pos_haud.Hold_Item, pos_haud.sa_discECard, pos_haud.HoldItemQty, pos_haud.WalkIn, pos_haud.Cust_Sig,  
pos_haud.sa_Round, pos_haud.Balance_Point, pos_haud.Total_Outstanding, pos_haud.Total_ItemHold_Qty, pos_haud.Total_Prepaid_Amt,  
pos_haud.Total_Voucher_Avalable, pos_haud.Total_Course_Summary, pos_haud.Total_CN_Amt, pos_haud.Previous_pts, pos_haud.Today_pts,  
pos_haud.Total_Balance_pts, pos_haud.Trans_User_Login, pos_haud.ID,   
pos_haud.SA_TransacNo_Ref, pos_haud.SA_TransacNo_Type, pos_haud.Cust_Sig_Path, pos_haud.Trans_Reason, pos_haud.Trans_Remark,  
pos_haud.Trans_RW_Point_Ratio, pos_haud.SA_Trans_DO_No, pos_haud.SA_TransacNo_Title,   
pos_haud.IssuesTrans_User_Login, pos_haud.Trans_PackageCode, pos_haud.Trans_Value, pos_haud.Trans_Pay, pos_haud.Trans_Outstanding,  
pos_haud.Used_pts, pos_haud.Earn_pts, pos_haud.Expire_Soon_Date_1, pos_haud.Expire_Soon_Point_1, pos_haud.Expire_Soon_Date_2,  
pos_haud.Expire_Soon_Point_2, pos_haud.Expire_Soon_Date_3, pos_haud.Expire_Soon_Point_3, pos_haud.Expire_Soon_Date_4, pos_haud.Expire_Soon_Point_4,  
pos_haud.Expire_Soon_Date_5, pos_haud.Expire_Soon_Point_5, pos_haud.Expire_Soon_Remark, pos_haud.Expire_Soon_Remark_Point,   
pos_taud.pay_amt, PAYTABLE.GT_Group, Customer_Class.Class_Code AS ClassCode, Customer_Class.Class_Desc AS ClassDesc, Prepaid_Account.PP_AMT,  
Prepaid_Account.Line_No, Prepaid_Account.TopUp_AMT, Prepaid_Account.TopUp_No, Prepaid_Account.ITEM_NO  
FROM Customer_Class RIGHT OUTER JOIN  
pos_haud INNER JOIN  
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno   
INNER JOIN    
pos_daud ON pos_haud.sa_transacno = pos_daud.sa_transacno    
LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit] FROM         
pos_daud INNER JOIN   
 
 Deposit_Account ON pos_daud.sa_transacno = Deposit_Account.sa_transacno   
 
  Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno And     
T0.dt_LineNo=pos_daud.dt_LineNo   
INNER JOIN  
Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code INNER JOIN  
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN  
PAYTABLE ON pos_taud.pay_type = PAYTABLE.pay_code LEFT OUTER JOIN  
Prepaid_Account ON pos_haud.sa_transacno = Prepaid_Account.PP_NO ON Customer_Class.Class_Code = Customer.Cust_Class  
where pos_daud.Record_Detail_Type = 'TP PREPAID'  
And  
pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate     
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))    
order by [Qty]  
END

-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_TopSalesPackageReport1')
BEGIN
DROP PROCEDURE Web_TopSalesPackageReport1
END
GO 
CREATE PROCEDURE Web_TopSalesPackageReport1        
 @FromDate nvarchar(10),        
 @ToDate nvarchar(10),        
 @Site nvarchar(Max),        
 @ShowFOC  nvarchar(1),        
 @SortBy  nvarchar(10)         
         
AS        
        
Declare @FDate DATETIME        
Declare @TDate DATETIME        
SET @FDate=Convert(Datetime,@FromDate,103)        
SET @TDate=Convert(Datetime,@ToDate,103)        
      
IF @SortBy='Amount'        
BEGIN       
SELECT Item_SiteList.ItemSite_Code AS SiteCode, pos_daud.dt_no, pos_daud.mac_code, pos_daud.sa_date, pos_daud.sa_time, pos_daud.cas_logno,    
pos_daud.sa_transacno, pos_daud.dt_status, pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice, pos_daud.dt_amt,    
pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent, pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,    
pos_daud.dt_StaffName, pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode, pos_daud.ItemSite_Code, pos_daud.dt_LineNo,    
pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark, pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment, pos_daud.Next_Appt,    
pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out, pos_daud.Issue_Date, pos_daud.Hold_Item, pos_daud.HoldItemQty,    
pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done, pos_daud.First_Trmt_Done_Staff_Code,    
pos_daud.First_Trmt_Done_Staff_Name, pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,    
pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code, pos_daud.TopUp_Product_Treat_Code,    
pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code, pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No,    
pos_daud.Update_Prepaid_Bonus, pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,     
pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,    
 pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, pos_daud.dt_GrossAmt,    
 pos_daud.dt_TopUp_Old_Outs_Amt, pos_daud.dt_TopUp_New_Outs_Amt, pos_daud.dt_TD_Tax_Amt, Employee.Display_Name AS StaffName,    
pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, pos_haud.sa_status AS SA_STATUS, Customer.Cust_code AS Cust_Code,    
Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, Customer_Class.Class_Desc AS ClassDesc, Item_Dept.itm_desc AS DeptDesc,    
Item_Brand.itm_desc AS BrandDesc, Item_Range.itm_desc AS RangeDesc, Stock.Item_Desc, Stock.Rpt_Code, pos_haud.SA_TransacNo_Ref    
FROM Item_Brand RIGHT OUTER JOIN    
pos_daud INNER JOIN    
Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN    
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN    
--LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit] FROM         pos_daud INNER JOIN                       Deposit_Account ON pos_daud.TopUp_Product_Treat_Code = Deposit_Account.Treat_Code AND       
--       pos_daud.sa_transacno = Deposit_Account.Ref_Code WHERE     (pos_daud.Record_Detail_Type = 'TP PRODUCT')  Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno And       
--T0.dt_LineNo=pos_daud.dt_LineNo   Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN    
Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code ON Item_Brand.itm_code = Stock.item_Brand LEFT OUTER JOIN    
Item_Range ON Stock.Item_Range = Item_Range.itm_code LEFT OUTER JOIN    
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN    
Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code    
WHERE (LEFT(pos_daud.dt_itemno, 1) = '1')   
---and pos_daud.Record_Detail_Type = 'TP SERVICE'    
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate         
And ((@Site='') OR ((@Site<>'')    
And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site        
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))        
order by pos_daud.dt_amt      
end      
ELSE      
BEGIN      
    
SELECT Item_SiteList.ItemSite_Code AS SiteCode, pos_daud.dt_no, pos_daud.mac_code, pos_daud.sa_date, pos_daud.sa_time, pos_daud.cas_logno,    
pos_daud.sa_transacno, pos_daud.dt_status, pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice, pos_daud.dt_amt,    
pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent, pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,    
pos_daud.dt_StaffName, pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode, pos_daud.ItemSite_Code, pos_daud.dt_LineNo,    
pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark, pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment, pos_daud.Next_Appt,    
pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out, pos_daud.Issue_Date, pos_daud.Hold_Item, pos_daud.HoldItemQty,    
pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done, pos_daud.First_Trmt_Done_Staff_Code,    
pos_daud.First_Trmt_Done_Staff_Name, pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,    
pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code, pos_daud.TopUp_Product_Treat_Code,    
pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code, pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No,    
pos_daud.Update_Prepaid_Bonus, pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,     
pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,    
 pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, pos_daud.dt_GrossAmt,    
 pos_daud.dt_TopUp_Old_Outs_Amt, pos_daud.dt_TopUp_New_Outs_Amt, pos_daud.dt_TD_Tax_Amt, Employee.Display_Name AS StaffName,    
pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, pos_haud.sa_status AS SA_STATUS, Customer.Cust_code AS Cust_Code,    
Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, Customer_Class.Class_Desc AS ClassDesc, Item_Dept.itm_desc AS DeptDesc,    
Item_Brand.itm_desc AS BrandDesc, Item_Range.itm_desc AS RangeDesc, Stock.Item_Desc, Stock.Rpt_Code, pos_haud.SA_TransacNo_Ref    
FROM Item_Brand RIGHT OUTER JOIN    
pos_daud INNER JOIN    
Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN    
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN    
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN    
Item_Dept ON Stock.Item_Dept = Item_Dept.itm_code ON Item_Brand.itm_code = Stock.item_Brand LEFT OUTER JOIN    
Item_Range ON Stock.Item_Range = Item_Range.itm_code LEFT OUTER JOIN    
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN    
Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code    
WHERE (LEFT(pos_daud.dt_itemno, 1) = '1')    
---and pos_daud.Record_Detail_Type = 'TP SERVICE'    
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate         
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site        
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))        
order by pos_daud.dt_qty       
 END


----------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_TopSalesProductReport1')
BEGIN
DROP PROCEDURE Web_TopSalesProductReport1
END
GO 

CREATE PROCEDURE Web_TopSalesProductReport1    
 @FromDate nvarchar(10),    
 @ToDate nvarchar(10),    
 @Site nvarchar(Max),    
 @Brand nvarchar(Max),    
 @Range nvarchar(Max),     
 @ShowFOC  nvarchar(1),    
 @SortBy  nvarchar(10)     
     
AS    
    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate,103)    
SET @TDate=Convert(Datetime,@ToDate,103)    
  
IF @SortBy='Amount'    
BEGIN   
SELECT     
pos_haud.ItemSite_Code ,    
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,    
Item_Brand.itm_desc as [Brand],     
Item_Range.itm_desc [Range],    
pos_daud.dt_qty as [Qty],     
pos_daud.dt_price * pos_daud.dt_qty as [amount],    
pos_daud.dt_deposit+ISNULL(T0.Deposit,0) as [Paid],    
pos_daud.dt_deposit as [deposit],  
(pos_daud.dt_price * pos_daud.dt_qty)-(pos_daud.dt_deposit+ISNULL(T0.Deposit,0)) as [Outstanding]    
FROM pos_haud INNER JOIN    
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    
pos_daud ON pos_haud.sa_transacno = pos_daud.sa_transacno    
LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit] FROM         
pos_daud INNER JOIN                       Deposit_Account ON pos_daud.TopUp_Product_Treat_Code = Deposit_Account.Treat_Code AND     
       pos_daud.sa_transacno = Deposit_Account.Ref_Code WHERE     (pos_daud.Record_Detail_Type = 'TP PRODUCT')  
Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno And     
T0.dt_LineNo=pos_daud.dt_LineNo    
INNER JOIN Stock ON pos_daud.dt_itemno = Stock.item_code + '0000'    
INNER JOIN Item_Brand ON Stock.item_Brand = Item_Brand.itm_code     
INNER JOIN Item_Range ON Stock.Item_Range = Item_Range.itm_code     
Where pos_daud.Record_Detail_Type='PRODUCT'    
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate     
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
And ((@Brand='') OR ((@Brand<>'') And item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand    
And ((@Range='') OR ((@Range<>'') And Item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range    
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))    
--)X    
Group By     
pos_haud.ItemSite_Code,     
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,    
Item_Brand.itm_desc ,     
Item_Range.itm_desc ,  
pos_daud.dt_qty,  
pos_daud.dt_price,  
pos_daud.dt_deposit,  
t0.deposit  
Order By [amount] DESC,[Qty] DESC  
END  
ELSE    
BEGIN    
SELECT     
pos_haud.ItemSite_Code ,    
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,    
Item_Brand.itm_desc as [Brand],     
Item_Range.itm_desc [Range],    
pos_daud.dt_qty as [Qty],     
pos_daud.dt_price * pos_daud.dt_qty as [amount],    
pos_daud.dt_deposit+ISNULL(T0.Deposit,0) as [Paid],    
pos_daud.dt_deposit as [deposit],  
(pos_daud.dt_price * pos_daud.dt_qty)-(pos_daud.dt_deposit+ISNULL(T0.Deposit,0)) as [Outstanding]    
FROM pos_haud INNER JOIN    
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    
pos_daud ON pos_haud.sa_transacno = pos_daud.sa_transacno    
LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit] FROM         
pos_daud INNER JOIN                       Deposit_Account ON pos_daud.TopUp_Product_Treat_Code = Deposit_Account.Treat_Code AND     
       pos_daud.sa_transacno = Deposit_Account.Ref_Code WHERE     (pos_daud.Record_Detail_Type = 'TP PRODUCT')  
Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno And     
T0.dt_LineNo=pos_daud.dt_LineNo    
INNER JOIN Stock ON pos_daud.dt_itemno = Stock.item_code + '0000'    
INNER JOIN Item_Brand ON Stock.item_Brand = Item_Brand.itm_code     
INNER JOIN Item_Range ON Stock.Item_Range = Item_Range.itm_code     
Where pos_daud.Record_Detail_Type='PRODUCT'    
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate     
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
And ((@Brand='') OR ((@Brand<>'') And item_Brand.itm_code In (Select Item From dbo.LISTTABLE(@Brand,',')))) --Brand    
And ((@Range='') OR ((@Range<>'') And Item_Range.itm_code In (Select Item From dbo.LISTTABLE(@Range,',')))) --Range    
AND (@ShowFOC='N' OR ( @ShowFOC='Y' AND (pos_daud.dt_itemdesc NOT LIKE '%FOC%')))    
--)X    
Group By     
pos_haud.ItemSite_Code,     
pos_haud.sa_transacno_ref ,    
pos_daud.dt_itemno ,     
pos_daud.dt_itemdesc ,    
Item_Brand.itm_desc ,     
Item_Range.itm_desc ,  
pos_daud.dt_qty,  
pos_daud.dt_price,  
pos_daud.dt_deposit,  
t0.deposit  
Order By [Qty] DESC,[amount] DESC  
END
---------------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionReport')
BEGIN
DROP PROCEDURE Web_DailyCollectionReport
END
GO 
   
CREATE  PROCEDURE Web_DailyCollectionReport
 @FromDate nvarchar(10),    
 @ToDate nvarchar(10),    
 @PayGroup nvarchar(Max),    
 @Site nvarchar(Max)    
AS    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate,103)    
SET @TDate=Convert(Datetime,@ToDate,103)    
SELECT distinct pos_daud.dt_no,    
pos_haud.ItemSite_Code [Outlet],    
pos_taud.pay_Desc [payTypes],    
pos_haud.sa_date [payDate],      
pos_haud.SA_TransacNo_Ref [invoiceRef],     
Customer.Cust_code [customerCode],    
Customer.Cust_name [customer],     
isnull(pos_daud.dt_itemdesc,'') [ItemName],    
--'' [ItemName],    
--(pos_taud.pay_actamt-pos_taud.PAY_GST)  [beforeGST] ,    
--(pos_taud.pay_actamt- (case when paytable.GT_Group='GT1' then (pos_taud.pay_actamt/ 107) * 7 else 0 end ) )  [beforeGST] , 
case when (select isactive from GST_Setting)=1 then   
round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else
 pos_taud.PAY_GST End) - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else pos_taud.PAY_GST End) )/100  +0 , 3)
 else
 pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End ) 
 end
 as  [beforeGST],    
--pos_taud.PAY_GST [GST],    
--(case when paytable.GT_Group='GT1' then (pos_taud.pay_actamt * 7 / 100) else 0 end ) [GST],    
--(case when paytable.GT_Group='GT1' then (pos_taud.pay_actamt/ 107) * 7  else 0 end ) [GST],    
--Convert(Decimal(19,3),(pos_taud.pay_actamt/107)*7) [GST],    
Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then pos_taud.PAY_GST else 
(CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else pos_taud.PAY_GST End) end) [GST],    
--(pos_taud.pay_actamt) [afterGST]    
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [afterGST]    
FROM pos_haud INNER JOIN    
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code     
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE    
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo    
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate     
and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )  and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0    
--and pos_haud.SA_TransacNo_Type IN ('Receipt','Void Transaction')    
--and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )     
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
--And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Desc In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup    
And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup 
------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionReport2') -- todo: check this
BEGIN
DROP PROCEDURE Web_DailyCollectionReport2
END
GO 
CREATE     PROCEDURE Web_DailyCollectionReport2                
 @FromDate nvarchar(10),                
 @ToDate nvarchar(10),                
 @PayGroup nvarchar(Max),                
 @PayGroup1 nvarchar(Max),    
 @Site nvarchar(Max)                
AS                
Declare @FDate DATETIME                
Declare @TDate DATETIME                
SET @FDate=Convert(Datetime,@FromDate,103)                
SET @TDate=Convert(Datetime,@ToDate,103)                
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

case when (select isactive from GST_Setting)=1 then              
sum(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then           
(pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else           
pos_taud.PAY_GST End) - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0          
 Else pos_taud.PAY_GST End) )/100  +0 , 3)) 
 else
 sum(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then           
(pos_taud.pay_actamt) Else 0 End )) 
 end
 [beforeGST],                
          
sum(Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then           
pos_taud.PAY_GST else (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else           
pos_taud.PAY_GST End) end)) [GST],                
          
sum(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then           
(pos_taud.pay_actamt) Else 0 End ))   [afterGST]               
           
FROM pos_haud INNER JOIN                
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno                 
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code                 
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE                
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo                
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate                 
and paytable.pay_code in (select pay_code from paytable)  and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0                
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site                
And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup             
group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group,pos_haud.SA_TransacNo_Ref,pos_haud.sa_custno,
pos_haud.sa_custname,pos_daud.dt_itemdesc          
order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc 
----------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType1')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType1
END
GO 

CREATE  PROCEDURE Web_SpecialTransactionType1         
@fromDate nvarchar(50),                  
@toDate nvarchar(50),                  
@fromSite nvarchar(255),     
@toSite nvarchar(255)       
 AS       
 SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,      
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],       
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,      
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,       
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,       
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,       
  pos_daud.dt_StaffName, pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,      
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,      
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,       
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,       
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,      
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,       
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,       
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,      
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,      
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,       
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,      
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,      
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,      
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                     
         Employee.Display_Name AS StaffName, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
pos_haud.sa_status AS SA_STATUS,                                                      
(SELECT CASE        
       --WHEN (pos_haud.sa_status like 'SA') THEN 'FOC'        
       --WHEN pos_haud.sa_status like 'VT' THEN 'Void'        
       --WHEN pos_daud.dt_status like 'EX' THEN 'Exchange' 
       WHEN (pos_daud.dt_status like 'SA') THEN 'FOC'        
       WHEN pos_daud.dt_status like 'VT' THEN 'Void'        
       WHEN pos_daud.dt_status like 'EX' THEN 'Exchange'            
        END AS OType) as OType,                              
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM           
pos_daud INNER JOIN                         
Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND   
  
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN                            
 pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN                             
 Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN                             
 Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN       
 Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN Item_SiteList ON 
pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code       
 WHERE    (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate) + ' 00:00:00') AND        
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate) + ' 23:59:59') 
AND        
(pos_haud.ItemSite_Code >= @fromSite) AND        
(pos_haud.ItemSite_Code <= @toSite) 
AND         
(pos_haud.sa_status <> 'PP') 
--AND (LEFT(pos_haud.Void_RefNo, 2) <> 'PP') 
AND               
(pos_daud.dt_itemdesc LIKE '%(FOC)%' or         
(pos_daud.dt_status LIKE 'VT%') or (pos_daud.dt_status like 'EX%')) 
AND         
 (pos_daud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND         
(pos_daud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND          
(pos_daud.ItemSite_Code >= @fromSite) AND         
(pos_daud.ItemSite_Code <= @toSite ) AND 
(pos_haud.sa_status <> 'PP') AND         
        
(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT%') or        
(pos_daud.dt_status like 'EX%')) AND (pos_haud.Void_RefNo IS NULL)        
 order by pos_daud.sa_date,dt_status,dt_LineNo          
---------
---------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType2')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType2
END
GO 

CREATE  PROCEDURE Web_SpecialTransactionType2     
@fromDate nvarchar(50),              
@toDate nvarchar(50),                          
@fromSite nvarchar(255),     
@toSite nvarchar(255)     
 AS     
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,  
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],   
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,   
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,   
  pos_daud.dt_StaffName as [StaffName], pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,   
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,   
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,  
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,   
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,   
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,  
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,  
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,  
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,  
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                 
         Employee.Display_Name AS StaffName1, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
pos_haud.sa_status AS SA_STATUS,                                                  
         (SELECT CASE    
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'    
       WHEN pos_daud.dt_status='VT' THEN 'Void'    
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'    
        END AS OType) as OType,                          
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode,  
 Customer_Class.Class_Desc AS ClassDesc FROM         pos_daud INNER JOIN    
   Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND  
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN    
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN    
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' 
LEFT OUTER JOIN     
 Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN      
   Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE      
    (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND      
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND      
(pos_haud.ItemSite_Code >= @fromSite) AND      
(pos_haud.ItemSite_Code <= @toSite) AND       
(pos_haud.sa_status <> 'PP') AND       
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND       
      
(pos_daud.dt_itemdesc LIKE '%(FOC)%' or       
(pos_daud.dt_status LIKE 'VT')) OR       
 (pos_daud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND       
(pos_daud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND        
(pos_daud.ItemSite_Code >= @fromSite) AND       
(pos_daud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP') AND       
      
(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT')      
) AND (pos_haud.Void_RefNo IS NULL)      
 order by pos_daud.sa_date,dt_status,dt_LineNo 
------
------
 CREATE or alter PROCEDURE Web_SpecialTransactionType3    
@fromDate nvarchar(50),              
@toDate nvarchar(50),                          
@fromSite nvarchar(255),     
@toSite nvarchar(255)     
 AS     
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,  
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],   
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,   
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,   
  pos_daud.dt_StaffName as [StaffName], pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,   
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,   
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,  
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,   
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,   
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,  
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,  
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,  
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,  
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                 
         Employee.Display_Name AS StaffName1, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
pos_haud.sa_status AS SA_STATUS,                                                  
       (SELECT CASE      
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'      
       WHEN pos_daud.dt_status='VT' THEN 'Void'      
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'      
        END AS OType) as OType,                            
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM         pos_daud INNER JOIN                       Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND 
  
    
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN                       pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno 
INNER JOIN                       Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN      
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN     Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code 
LEFT OUTER JOIN       
 Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE         
(pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ '00:00:00') AND        
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ '23:59:59') AND        
(pos_haud.ItemSite_Code >= @fromSite) AND        
(pos_haud.ItemSite_Code <= @toSite) AND         
(pos_haud.sa_status <> 'PP') AND         
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND         
        
--(pos_daud.dt_itemdesc LIKE '%(FOC)%' or (pos_daud.dt_status = 'EX') or        
--(pos_daud.dt_status LIKE 'VT')) OR (pos_daud.dt_itemdesc LIKE '%(FOC)%'  or        
(pos_daud.dt_itemdesc LIKE '%(FOC)%') or        
      
 (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ '00:00:00') AND         
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ '23:59:59') AND          
(pos_haud.ItemSite_Code >= @fromSite) AND         
(pos_haud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP') AND         
        
--(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT') or        
--(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)        
(pos_daud.dt_itemdesc LIKE '%(FOC)%') AND (pos_haud.Void_RefNo IS NULL)        
        
 order by pos_daud.sa_date,dt_status,dt_LineNo 
------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType4')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType4
END
GO 

 CREATE  PROCEDURE Web_SpecialTransactionType4  
@fromDate nvarchar(50),              
@toDate nvarchar(50),                          
@fromSite nvarchar(255),     
@toSite nvarchar(255)     
 AS     
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,  
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],   
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,   
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,   
  pos_daud.dt_StaffName as [StaffName], pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,   
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,   
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,  
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,   
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,   
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,  
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,  
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,  
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,  
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                 
         Employee.Display_Name AS StaffName1, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
pos_haud.sa_status AS SA_STATUS,                                                  
      (SELECT CASE    
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'    
       WHEN pos_daud.dt_status='VT' THEN 'Void'    
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'    
        END AS OType) as OType,                          
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM         pos_daud INNER JOIN                       
Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND 
  
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN    
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN      
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN                       
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT
OUTER JOIN 
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN                       
Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE        
    
(pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND      
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND      
(pos_haud.ItemSite_Code >= @fromSite) AND      
(pos_haud.ItemSite_Code <= @toSite) AND       
(pos_haud.sa_status <> 'PP') AND       
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND       
      
--(pos_daud.dt_itemdesc LIKE '%(FOC)%' or (pos_daud.dt_status = 'EX') or      
--(pos_daud.dt_status LIKE 'VT')) OR ((pos_daud.dt_status = 'EX') or      
(pos_daud.dt_status LIKE 'VT') OR        
 (pos_daud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND       
(pos_daud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND        
(pos_daud.ItemSite_Code >= @fromSite) AND     
(pos_daud.ItemSite_Code <= @toSite) AND 
(pos_haud.sa_status <> 'PP') AND       
      
--(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT') or      
--(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)      
((pos_daud.dt_status LIKE 'VT') or      
(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)      
 order by pos_daud.sa_date,dt_status,dt_LineNo 
------
------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType7')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType7
END
GO 

CREATE PROCEDURE Web_SpecialTransactionType7  
@fromDate nvarchar(50),              
@toDate nvarchar(50),                          
@fromSite nvarchar(255),     
@toSite nvarchar(255)     
 AS     
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,  
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],   
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,   
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,   
  pos_daud.dt_StaffName as [StaffName], pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,   
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,   
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,  
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,   
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,   
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,  
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,  
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,  
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,  
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                 
         Employee.Display_Name AS StaffName1, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
pos_haud.sa_status AS SA_STATUS,                                                  
      (SELECT CASE    
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'    
       WHEN pos_daud.dt_status='VT' THEN 'Void'    
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'    
        END AS OType) as OType,                          
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM         pos_daud INNER JOIN                       
Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND 
  
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN                       
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN                       
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN    
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN     
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN     
 Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE       
(pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND      
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND      
(pos_haud.ItemSite_Code >= @fromSite) AND      
(pos_haud.ItemSite_Code <= @toSite) AND       
(pos_haud.sa_status <> 'PP') AND       
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND       
      
--(pos_daud.dt_itemdesc LIKE '%(FOC)%' or (pos_daud.dt_status = 'EX') or      
--(pos_daud.dt_status LIKE 'VT')) OR (pos_daud.dt_itemdesc LIKE '%(FOC)%'  or      
(pos_daud.dt_itemdesc LIKE '%(FOC)%' or (pos_daud.dt_status = 'EX')) or      
    
 (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND       
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND        
(pos_haud.ItemSite_Code >= @fromSite) AND       
(pos_haud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP') AND       
      
--(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT') or      
--(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)      
(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or      
(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)      
      
 order by pos_daud.sa_date,dt_status,dt_LineNo

-----------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType8')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType8
END
GO 

CREATE  PROCEDURE Web_SpecialTransactionType8   
 @fromDate nvarchar(50),            
@toDate nvarchar(50),            
@fromSite nvarchar(255),   
@toSite nvarchar(255)   
 AS   
 SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc, pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) 
as [sa_date], pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice, pos_daud.dt_amt, pos_daud.dt_qty, 
  pos_daud.dt_discAmt, pos_daud.dt_discPercent, pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, 
  pos_daud.dt_Staffno, pos_daud.dt_StaffName, pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,                        
pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark, pos_daud.dt_UOM, pos_daud.IsFoc, 
  pos_daud.Item_Remarks, pos_daud.Next_Payment,pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, 
pos_daud.Hold_Item_Out, pos_daud.Issue_Date, pos_daud.Hold_Item, pos_daud.HoldItemQty,
 pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done, pos_daud.First_Trmt_Done_Staff_Code, 
 pos_daud.First_Trmt_Done_Staff_Name,pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, 
 pos_daud.Trmt_Done_Staff_Name, pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,
 pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code, 
 pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No,pos_daud.Update_Prepaid_Bonus, pos_daud.Deduct_Commission, 
 pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect, pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, 
 pos_daud.COMPOUND_CODE,pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, 
 pos_daud.T2_Tax_Amt, pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,Employee.Display_Name AS StaffName, pos_haud.sa_custno AS Cust_Code,
  pos_haud.sa_custname AS Cust_Name, pos_haud.sa_status AS SA_STATUS,
                                                  
(SELECT CASE  
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'  
       WHEN pos_daud.dt_status='VT' THEN 'Void'  
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'  
        END AS OType) as OType,                        
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM 
 pos_daud INNER JOIN                       Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND 
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN 
 pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN 
  Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN                       
  Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN                       
  Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN                       
  Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE   
     (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND    
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND    
(pos_haud.ItemSite_Code >= @fromSite) AND    
(pos_haud.ItemSite_Code <= @toSite) AND     
(pos_haud.sa_status <> 'PP') AND     
-- (LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND     
      
 (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND     
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND      
(pos_haud.ItemSite_Code >= @fromSite) AND     
(pos_haud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP')     
 order by dt_LineNo 

----------

------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType6')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType6
END
GO 

CREATE  PROCEDURE Web_SpecialTransactionType6  
@fromDate nvarchar(50),              
@toDate nvarchar(50),                          
@fromSite nvarchar(255),     
@toSite nvarchar(255)     
 AS     
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc,pos_haud.SA_TransacNo_Ref,  
  pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103) as [sa_date],   
 pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno, pos_daud.dt_status,  
  pos_daud.dt_itemno, pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
  pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,   
  pos_daud.dt_discDesc, pos_daud.dt_discno, pos_daud.dt_remark, pos_daud.dt_Staffno,   
  pos_daud.dt_StaffName as [StaffName], pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  
  pos_daud.ItemSite_Code, pos_daud.dt_LineNo, pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark,  
  pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.Next_Payment,   
  pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time, pos_daud.Hold_Item_Out,   
  pos_daud.Issue_Date, pos_daud.Hold_Item,pos_daud.HoldItemQty,  
  pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done,   
  pos_daud.First_Trmt_Done_Staff_Code, pos_daud.First_Trmt_Done_Staff_Name,   
   pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code, pos_daud.Trmt_Done_Staff_Name,  
    pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,  
    pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
    pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No, pos_daud.Update_Prepaid_Bonus,  
     pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,  
     pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,  
      pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code, pos_daud.T2_Tax_Amt, 
      pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,                
         Employee.Display_Name AS StaffName1, pos_haud.sa_custno AS Cust_Code, pos_haud.sa_custname AS Cust_Name, 
         pos_haud.sa_status AS SA_STATUS,                                                  
      (SELECT CASE      
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'      
       WHEN pos_daud.dt_status='VT' THEN 'Void'      
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'      
        END AS OType) as OType,                            
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode, 
Customer_Class.Class_Desc AS ClassDesc FROM         
pos_daud INNER JOIN  Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND
  
    
LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN                       
pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN                       
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN      
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN     
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN       
 Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE         
(pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND        
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND        
(pos_haud.ItemSite_Code >= @fromSite) AND        
(pos_haud.ItemSite_Code <= @toSite) AND         
(pos_haud.sa_status <> 'PP') AND         
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND         
        
--(pos_daud.dt_itemdesc LIKE '%(FOC)%' or (pos_daud.dt_status = 'EX') or        
--(pos_daud.dt_status LIKE 'VT')) OR (pos_daud.dt_itemdesc LIKE '%(FOC)%'  or        
   
((pos_daud.dt_status LIKE 'VT')) OR   
 (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND         
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND          
(pos_haud.ItemSite_Code >= @fromSite) AND         
(pos_haud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP') AND         
        
--(pos_daud.dt_itemdesc LIKE '%(FOC)%'  or (pos_daud.dt_status LIKE 'VT') or        
--(pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)        
(pos_daud.dt_status LIKE 'VT') AND (pos_haud.Void_RefNo IS NULL)    
      
        
 order by pos_daud.sa_date,dt_status,dt_LineNo 
------
------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SpecialTransactionType5')
BEGIN
DROP PROCEDURE Web_SpecialTransactionType5
END
GO 

CREATE PROCEDURE Web_SpecialTransactionType5    
 @fromDate nvarchar(50),                  
@toDate nvarchar(50),                  
@fromSite nvarchar(255),         
@toSite nvarchar(255)          
AS         
SELECT     Item_SiteList.ItemSite_Desc AS SiteDesc, pos_daud.dt_no, pos_daud.mac_code, Convert(Date,pos_daud.sa_date,103)  [sa_date], 
pos_daud.sa_time, pos_daud.cas_logno, pos_daud.sa_transacno,
pos_daud.dt_status,  pos_daud.dt_itemno,pos_daud.dt_itemdesc, pos_daud.dt_price, pos_daud.dt_PromoPrice,   
pos_daud.dt_amt, pos_daud.dt_qty, pos_daud.dt_discAmt, pos_daud.dt_discPercent,  pos_daud.dt_discDesc, pos_daud.dt_discno,  
 pos_daud.dt_remark, pos_daud.dt_Staffno,pos_daud.dt_StaffName as [StaffName],   
 pos_daud.dt_Reason, pos_daud.dt_DiscUser, pos_daud.dt_ComboCode,  pos_daud.ItemSite_Code, pos_daud.dt_LineNo,   
 pos_daud.dt_StockUpdate, pos_daud.dt_StockRemark, pos_daud.dt_UOM, pos_daud.IsFoc, pos_daud.Item_Remarks, pos_daud.    
Next_Payment,pos_daud.Next_Appt, pos_daud.dt_TransacAmt, pos_daud.dt_deposit, pos_daud.Appt_Time,  
 pos_daud.Hold_Item_Out, pos_daud.Issue_Date, pos_daud.Hold_Item, pos_daud.HoldItemQty,       
 pos_daud.ST_Ref_TreatmentCode, pos_daud.Item_Status_Code, pos_daud.First_Trmt_Done, pos_daud.First_Trmt_Done_Staff_Code,  
  pos_daud.First_Trmt_Done_Staff_Name,                        pos_daud.Record_Detail_Type, pos_daud.Trmt_Done_Staff_Code,     
 pos_daud.Trmt_Done_Staff_Name, pos_daud.Trmt_Done_ID, pos_daud.Trmt_Done_Type, pos_daud.TopUp_Service_Trmt_Code,       
 pos_daud.TopUp_Product_Treat_Code, pos_daud.TopUp_Prepaid_Trans_Code, pos_daud.TopUp_Prepaid_Type_Code,   
 pos_daud.Voucher_Link_Cust, pos_daud.Voucher_No,       
 pos_daud.Update_Prepaid_Bonus, pos_daud.Deduct_Commission, pos_daud.Deduct_comm_refLine, pos_daud.GST_Amt_Collect,                          
pos_daud.TopUp_Prepaid_POS_Trans_LineNo, pos_daud.OPEN_PP_UID_REF, pos_daud.COMPOUND_CODE,        
 pos_daud.TopUp_Outstanding, pos_daud.T1_Tax_Code, pos_daud.T1_Tax_Amt, pos_daud.T2_Tax_Code,   
 pos_daud.T2_Tax_Amt, pos_daud.dt_GrossAmt, pos_daud.Trmt_Bal,   Employee.Display_Name AS StaffName1, pos_haud.sa_custno       
AS Cust_Code, pos_haud.sa_custname AS Cust_Name, pos_haud.sa_status AS SA_STATUS,                                                      
(SELECT CASE        
       WHEN (pos_daud.dt_status='SA') THEN 'FOC'        
       WHEN pos_daud.dt_status='VT' THEN 'Void'        
       WHEN pos_daud.dt_status='EX' THEN 'Exchange'        
        END AS OType) as OType,                              
Customer.Cust_code AS Cust_Code,Customer.Cust_name AS Cust_Name, Customer_Class.Class_Code AS ClassCode,   
Customer_Class.Class_Desc AS ClassDesc FROM         pos_daud INNER JOIN    
 Employee ON pos_daud.dt_Staffno = Employee.Emp_code AND LEFT(pos_daud.sa_transacno, 2) <> 'PP' INNER JOIN   
 pos_haud ON pos_daud.sa_transacno = pos_haud.sa_transacno INNER JOIN    
Customer ON pos_haud.sa_custno = Customer.Cust_code INNER JOIN        
Stock ON pos_daud.dt_itemno = Stock.item_code + '0000' LEFT OUTER JOIN   
Customer_Class ON Customer.Cust_Class = Customer_Class.Class_Code LEFT OUTER JOIN         
 Item_SiteList ON pos_daud.ItemSite_Code = Item_SiteList.ItemSite_Code WHERE           
(pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND          
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND          
(pos_haud.ItemSite_Code >= @fromSite) AND          
(pos_haud.ItemSite_Code <= @toSite) AND           
(pos_haud.sa_status <> 'PP') AND           
--(LEFT(pos_haud.Void_RefNo, 2) <> 'PP') AND           
((pos_daud.dt_status = 'EX')) OR      
 (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)+ ' 00:00:00') AND           
(pos_haud.sa_date <= CONVERT(DATETIME, @toDate)+ ' 23:59:59') AND            
(pos_haud.ItemSite_Code >= @fromSite) AND           
(pos_haud.ItemSite_Code <= @toSite) AND (pos_haud.sa_status <> 'PP') AND           
               
((pos_daud.dt_status = 'EX')) AND (pos_haud.Void_RefNo IS NULL)          
        
 order by pos_daud.sa_date,dt_status,dt_LineNo 
------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_ItemCollectionReport')
BEGIN
DROP PROCEDURE Web_ItemCollectionReport
END
GO 

CREATE PROCEDURE Web_ItemCollectionReport
@FromDate Varchar(10),  
@ToDate Varchar(10),  
@Site Varchar(max),  
@Type Varchar(10)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)  
  
  
IF OBJECT_ID('tempdb.#Data_ItemCollectionReport') IS NOT NULL DROP TABLE #Data_ItemCollectionReport  
Select   
X.item,  
X.itemDescription,  
X.itemSite_code [siteCode],   
X.ItemSite_Desc [siteName],  
Sum(X.[numItem]) [numItem],  
Sum(X.[numPaid]) [numPaid],  
Sum(X.[numFOC]) [numFOC],  
Sum(X.[totValue]) [totValue],  
Sum(X.[totDisc]) [totDisc],  
Sum(X.[potentialReceivable]) [potentialReceivable],  
Sum(X.[totReceivable]) [totReceivable]  
from (  
SELECT   
pos_daud.dt_itemno [item],   
pos_daud.dt_itemdesc [itemDescription],  
Item_SiteList.itemSite_code,  
Item_SiteList.ItemSite_Desc,  
pos_daud.dt_qty [numItem],   
Case When dt_itemdesc Not Like '%FOC%' Then  pos_daud.dt_qty Else 0 End [numPaid],   
Case When dt_itemdesc  Like '%FOC%' Then  pos_daud.dt_qty Else 0 End  [numFOC],   
Case When dt_itemdesc Not Like '%FOC%' Then  pos_daud.dt_price * pos_daud.dt_qty Else 0 End [totValue],  
Case When dt_itemdesc Not Like '%FOC%' Then  pos_daud.dt_discAmt * pos_daud.dt_qty  Else 0 End [totDisc],  
pos_daud.dt_TransacAmt AS [potentialReceivable],   
pos_daud.dt_deposit+ISNULL(T0.Deposit,0) AS [totReceivable]  
FROM pos_haud INNER JOIN  
Customer ON pos_haud.sa_custno = Customer.Cust_code   
INNER JOIN pos_daud ON pos_haud.sa_transacno = pos_daud.sa_transacno  
INNER JOIN Item_SiteList on pos_haud.ItemSite_Code=Item_SiteList.ItemSite_Code  
LEFT JOIN (SELECT Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo,Sum(Deposit) [Deposit]  
FROM         pos_daud INNER JOIN  
                      Deposit_Account ON pos_daud.TopUp_Product_Treat_Code = Deposit_Account.Treat_Code 
AND pos_daud.sa_transacno = Deposit_Account.Ref_Code  
WHERE     (pos_daud.Record_Detail_Type = 'TP PRODUCT')   
Group BY Deposit_Account.sa_Transacno,Deposit_Account.dt_LineNo) T0 ON T0.sa_Transacno=pos_daud.sa_transacno 
And T0.dt_LineNo=pos_daud.dt_LineNo  
Where pos_daud.Record_Detail_Type='PRODUCT'  
And pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate   
--And pos_haud.ItemSite_Code=@Site  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
)X  
Group By X.item,X.itemDescription,X.itemSite_code,X.ItemSite_Desc  


-------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_GSTReport')
BEGIN
DROP PROCEDURE Web_GSTReport
END
GO 

CREATE  PROCEDURE Web_GSTReport   
@fromDate nvarchar(50),            
@toDate nvarchar(50),            
@fromSite nvarchar(255),  
 @toSite nvarchar(255)   
AS    
SELECT     Convert(Date,pos_haud.sa_date,103) as [sa_date], pos_haud.ItemSite_Code, pos_haud.sa_transacno, 
 pos_haud.SA_TransacNo_Ref,  
 pos_haud.sa_custno, pos_haud.sa_custname, pos_taud.dt_lineno,  pos_taud.pay_type, pos_taud.pay_Desc, pos_taud.pay_actamt,   
pos_taud.Pay_GST_Amt_Collect, (pos_taud.pay_actamt+pos_taud.Pay_GST_Amt_Collect) as TotAmt,  PAYTABLE.GT_Group FROM pos_haud   
INNER JOIN  pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno   
INNER JOIN   
PAYTABLE ON pos_taud.pay_type = PAYTABLE.pay_code and PAYTABLE.pay_is_gst=1  
 WHERE     (pos_haud.sa_date >= CONVERT(DATETIME, @fromDate)) AND (pos_haud.sa_date <= CONVERT(DATETIME, @toDate))   
 AND (pos_haud.ItemSite_Code >= @fromSite) AND (pos_haud.ItemSite_Code <= @toSite)   
ORDER BY sa_date,pos_haud.ItemSite_Code,sa_transacno_ref,dt_lineno   

-------

  

--------   
      

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_TreatmentDoneReport')
BEGIN
DROP PROCEDURE Web_TreatmentDoneReport
END
GO 

  
CREATE PROCEDURE Web_TreatmentDoneReport 
@FromDate Varchar(10),
@ToDate Varchar(10),
@Site Varchar(max),
@Type Varchar(max)
  AS
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate + ' 00:00:00.000',103)    
SET @TDate=Convert(Datetime,@ToDate + ' 23:59:59.000',103) 
SELECT   distinct            
Convert(Date,pos_haud.sa_date,103) AS [invoiceDate],              
Convert(Date,Treatment_Account.sa_date,103) AS [usageDate],              
pos_haud_1.SA_TransacNo_Ref AS [usageRef],              
pos_haud.SA_TransacNo_Ref AS [invoiceRef],            
pos_haud.ItemSIte_Code as [Site_Code],               
Item_SiteList.ItemSite_Desc AS [site],             
Customer.Cust_name [custName],              
isnull(Customer.Cust_Refer,'') [custRef],              
Treatment_Account.User_Name [createdBy],             
(item_Class.itm_desc) [category],             
isnull((Item_Range.itm_desc),'')  [subCategory],                
Treatment_account.Description [itemName],             
Treatment.Service_ItemBarcode [skuCode],             
isnull(Treatment.Duration,0) 
[duration],             
Treatment_Account.Qty [usageQty],             
-1*Treatment_Account.Amount [unitValue],             
isnull(Item_Helper.Helper_Name,'') [therapists],                
(Select Count(*) from Item_Helper Where Helper_transacno=Treatment_Account.sa_transacno And Line_No=Treatment_Account.dt_LineNo)  [numTherapists],             
'' [SerPtType],                
isnull((Select distinct Item_Helper.WP1 from Item_Helper t1 Where t1.Helper_transacno=Treatment_Account.sa_transacno  
And t1.Line_No=Treatment_Account.dt_LineNo and t1.Helper_Name=Item_Helper.Helper_Name),'')  [SerPt],                
'' [remarks]                
FROM Treatment_Account INNER JOIN                   
pos_haud ON Treatment_Account.sa_transacno = pos_haud.sa_transacno INNER JOIN          
Item_Helper On Item_Helper.Helper_transacno=Treatment_Account.sa_transacno And   Item_Helper.Line_No=Treatment_Account.dt_LineNo  
INNER JOIN               
pos_haud AS pos_haud_1 ON Treatment_Account.sa_transacno = pos_haud_1.sa_transacno INNER JOIN             
Customer ON Treatment_Account.Cust_Code = Customer.Cust_code INNER JOIN             
Treatment ON Treatment.Treatment_ParentCode=Treatment_Account.Treatment_ParentCode And Treatment.status='Done' INNER JOIN             
Item_SiteList ON pos_haud_1.ItemSite_Code=Item_SiteList.ItemSite_Code INNER JOIN             
Stock ON Stock.item_code+'0000'=Treatment.Service_ItemBarcode INNER JOIN             
item_Class ON item_Class.itm_code=Stock.Item_Class INNER JOIN             
Item_Range ON Item_Range.itm_code=Stock.Item_Range             
WHERE (Treatment_Account.Type <> 'Deposit')             
And pos_haud.sa_date>=@FDate  And pos_haud.sa_date<=@TDate 
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site                    
order by therapists  





----------

 
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'SP_Birthday_Report')
BEGIN
DROP PROCEDURE SP_Birthday_Report
END
GO 

 
CREATE  PROCEDURE SP_Birthday_Report      
@FromDate Varchar(10),      
@ToDate Varchar(10),      
@Month decimal(18,0),    
@Site Varchar(MAX)      
AS      
BEGIN      
    
SELECT    Item_siteList.ItemSite_Desc as [Site_Desc] ,Customer.Cust_code, Customer.Cust_name, FORMAT(Customer.Cust_DOB,'dd-MMM-yyyy') as 
[Cust_DOB], Customer.Cust_phone2, isnull(Cust_TD.TD_Count,0) as [TD_Count]    
FROM         Customer     
inner join Item_siteList on Customer.cust_code like  + Item_siteList.ItemSite_Code  + '%'
 LEFT OUTER JOIN    
                          (SELECT     TOP (100) PERCENT Cust_Code, COUNT(*) AS TD_Count    
                            FROM          Treatment    
                            WHERE      (sa_status = 'SA') AND (Status = 'Done') AND (Treatment_Date >= @FromDate) AND (Treatment_Date <= @ToDate)    
                            GROUP BY Cust_Code    
                            ORDER BY Cust_Code) AS Cust_TD ON Customer.Cust_code = Cust_TD.Cust_Code     
WHERE    (Customer.DOB_status = 'True') AND (MONTH(Customer.Cust_DOB) = @Month) and Customer.cust_isactive = '1'     
And ((@Site='') OR ((@Site<>'')  And  Item_siteList.ItemSite_Code in (Select Item From dbo.LISTTABLE(@Site,','))))    
    
ORDER BY Item_siteList.ItemSite_Code,Customer.Cust_Name    
END    
    
  
----------


--------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionReport_For_Staff')
BEGIN
DROP PROCEDURE Web_SaleCollectionReport_For_Staff
END
GO 
create PROCEDURE [dbo].[Web_SaleCollectionReport_For_Staff]    
@Staff Varchar(max),    
@FromDate Varchar(10),    
@ToDate Varchar(10),    
@Site Varchar(max)  
AS    
    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
--SET @FDate=Convert(Datetime,dateadd(DAY,-30,getdate()),103)    
--SET @TDate=Convert(Datetime,getdate(),103)    
SET @FDate=Convert(Datetime,@FromDate,103)    
SET @TDate=Convert(Datetime,@ToDate,103)    
  
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport    
    
Select X.payDate,X.customer,X.invoiceRef,[payRef],isnull([CustRef],'') [CustRef],    
    
--STRING_SPLIT (X.payTypes,',') [payTypes],    
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],    
X.payTypes [payTypes],    
(case when X.[Group]='GT1' then 'Sales' else 'Non-Sales' end) as SalesGroup,    
X.ItemSite_Code [siteCode],    
X.ItemSite_Desc [siteName],    
sa_staffno,sa_staffname,    
isnull(SUM(X.amt),0) [amt],    
isnull(SUM(X.payCN),0) [payCN],    
isnull(SUM(X.payContra),0) [payContra],    
isnull(SUM(X.grossAmt),0) [grossAmt],    
isnull(MAX(X.taxes),0) [taxes],    
isnull(SUM(X.gstRate),0) [gstRate],    
isnull(SUM(X.netAmt),0) [netAmt],    
isnull(SUM(X.BankCharges),0) [BankCharges],    
isnull(SUM(X.comm),0) [comm],    
isnull(SUM(X.total),0) total      
from (    
SELECT     
ph.sa_staffno,ph.sa_staffname,    
convert (varchar,ph.sa_date,103)[payDate],     
Customer.Cust_name [customer],      
ph.SA_TransacNo_Ref [invoiceRef],     
ph.sa_transacno [payRef],Customer.Cust_Refer [CustRef],    
--pos_taud.pay_Desc [payTypes],    
pd.dt_itemdesc as [payTypes],    
--pos_taud.pay_actamt  [amt] ,     
0 [payContra],    
--paytable.GT_Group [Group],    
'' as [Group],    
--Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],    
0 as [payCN],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],    
0 as [grossAmt],    
--pos_taud.PAY_GST [taxes],    
0 as [taxes],    
--Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],    
0 as [gstRate],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],    
0 as [netAmt],    
0 [comm],    
--isnull(bank_charges,0) [BankCharges],    
0 as [BankCharges],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - isnull(bank_charges,0)+0 [total],    
pd.ItemSite_Code,Item_SiteList.ItemSite_Desc,    
round(((pd.dt_deposit/100*ms.ratio)),2) amt ,round(((pd.dt_deposit/100*ms.ratio)),2) [total]    
FROM pos_daud pd    
inner join multistaff ms on ms.sa_transacno = pd.sa_transacno and pd.dt_lineno = ms.dt_lineno    
inner join pos_haud ph on ph.sa_transacno = pd.sa_transacno    
--INNER JOIN pos_taud ON ph.sa_transacno = pos_taud.sa_transacno    
INNER JOIN Customer ON ph.sa_custno = Customer.Cust_code     
INNER JOIN Item_SiteList ON pd.ItemSite_Code = Item_SiteList.ItemSite_Code     
--INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE    
  
Where     
ms.emp_code in (select Emp_code from fmspw where pw_userlogin=@Staff) and pd.dt_deposit != 0     
And ((@Site='') OR ((@Site<>'') And pd.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
and pd.sa_date>=@FDate And pd.sa_date<=@TDate     
)X    
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,sa_staffno,sa_staffname,[payRef],[CustRef],X.[Group]   
order by X.payDate
----

---------- 
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionReport')
BEGIN
DROP PROCEDURE Web_SaleCollectionReport
END
GO 

CREATE PROCEDURE [dbo].[Web_SaleCollectionReport]  
@FromDate Varchar(10),  
@ToDate Varchar(10),  
@Site Varchar(10),  
@Type Varchar(10)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)  
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport  
  
Select X.payDate,X.customer,X.invoiceRef,  
--STRING_SPLIT (X.payTypes,',') [payTypes],  
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],  
X.payTypes [payTypes],  
SUM(X.amt) [amt],  
SUM(X.payCN) [payCN],  
SUM(X.payContra) [payContra],  
SUM(X.grossAmt) [grossAmt],  
MAX(X.taxes) [taxes],  
SUM(X.gstRate) [gstRate],  
SUM(X.netAmt) [netAmt],  
SUM(X.comm) [comm],  
SUM(X.total) total    
from (  
SELECT pos_haud.sa_date [payDate],    
Customer.Cust_name [customer],    
pos_haud.SA_TransacNo_Ref [invoiceRef],   
pos_taud.pay_Desc [payTypes],   
pos_taud.pay_actamt  [amt] ,   
0 [payContra],  
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  
pos_taud.PAY_GST [taxes],  
Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  
0 [comm],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST+0 [total]  
FROM pos_haud INNER JOIN  
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno   INNER JOIN  
Customer ON pos_haud.sa_custno = Customer.Cust_code   
Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate And pos_haud.ItemSite_Code=@Site)X  
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes  
----------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionSummaryReport')
BEGIN
DROP PROCEDURE Web_SaleCollectionSummaryReport
END
GO 

CREATE PROCEDURE Web_SaleCollectionSummaryReport
@FromDate Varchar(10),  
@ToDate Varchar(10),  
@Site Varchar(max),  
@Type Varchar(10),  
@PayMode Varchar(max)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)  
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport  
  
Select X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],  
  
--STRING_SPLIT (X.payTypes,',') [payTypes],  
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],  
X.payTypes [payTypes],  
(case when X.[Group]='GT1' then 'Sales' else 'Non-Sales' end) as SalesGroup,  
X.ItemSite_Code [siteCode],  
X.ItemSite_Desc [siteName],  
isnull(SUM(X.amt),0) [amt],  
isnull(SUM(X.payCN),0) [payCN],  
isnull(SUM(X.payContra),0) [payContra],  
isnull(SUM(X.grossAmt),0) [grossAmt],  
isnull(MAX(X.taxes),0) [taxes],  
isnull(SUM(X.gstRate),0) [gstRate],  
isnull(SUM(X.netAmt),0) [netAmt],  
isnull(SUM(X.BankCharges),0) [BankCharges],  
isnull(SUM(X.comm),0) [comm],  
isnull(SUM(X.total),0) total    
from (  
SELECT   
--pos_haud.sa_date [payDate],    
--CAST (pos_haud.sa_date AS DATE) [payDate],   
convert (varchar,pos_haud.sa_date,103)[payDate],   
Customer.Cust_name [customer],    
pos_haud.SA_TransacNo_Ref [invoiceRef],   
pos_haud.sa_transacno [payRef],Customer.Cust_Refer [CustRef],  
pos_taud.pay_Desc [payTypes],   
pos_taud.pay_actamt  [amt] ,   
0 [payContra],  
paytable.GT_Group [Group],  
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  
pos_taud.PAY_GST [taxes],  
Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 
Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  
0 [comm],  
round((isnull(bank_charges,0) * pos_taud.pay_actamt)/100 ,2) as [BankCharges],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' 
Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - round((isnull(bank_charges,0) * pos_taud.pay_actamt)/100 ,2) +0 [total],  
pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc  
FROM pos_haud   
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code   
INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code   
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE  
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate 
And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate --And pos_haud.ItemSite_Code=@Site  
--and pos_haud.SA_TransacNo_Type='Receipt'  
and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' ) and pos_haud.isVoid!=1  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
And ((@PayMode='') OR ((@PayMode<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayMode,',')))) --pay  
)X  
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,[payRef],[CustRef],X.[Group]  

----------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SaleCollectionReport_For_Mngr')
BEGIN
DROP PROCEDURE Web_SaleCollectionReport_For_Mngr
END
GO 


CREATE PROCEDURE Web_SaleCollectionReport_For_Mngr    
@FromDate Varchar(10),    
@ToDate Varchar(10),    
@Site Varchar(max),    
@staffCode Varchar(max)    
AS    
Declare @FDate DATETIME    
Declare @TDate DATETIME    
SET @FDate=Convert(Datetime,@FromDate,103)    
SET @TDate=Convert(Datetime,@ToDate,103)    
IF OBJECT_ID('tempdb.#Data_SaleCollectionReport') IS NOT NULL DROP TABLE #Data_SaleCollectionReport    
IF OBJECT_ID('tempdb.#a1') IS NOT NULL DROP TABLE #a1    
IF OBJECT_ID('tempdb.#a2') IS NOT NULL DROP TABLE #a2    
    
select distinct ms.sa_transacno,ms.item_code, employee.emp_name,  (case when emp_level_group.Group_Desc is null then 'PRIMARY' else 
emp_level_group.Group_Desc end) as Group_Desc,  round(ms.ratio,2)as ratio into #a1 from pos_daud pd  inner join multistaff 
  
    
ms on ms.sa_transacno = pd.sa_transacno and pd.dt_lineno = ms.dt_lineno inner join pos_haud ph on ph.sa_transacno = pd.sa_transacno 
inner join employee on ms.emp_code = employee.emp_code left join emp_level_group   
on ms.level_group_code=emp_level_group.Group_Code  
 --where ms.emp_code not in   --(SELECT     
--employee.emp_code    
--FROM pos_daud pd    
--inner join multistaff ms on ms.sa_transacno = pd.sa_transacno and pd.dt_lineno = ms.dt_lineno    
--inner join employee on ms.emp_code = employee.emp_code    
--inner join pos_haud ph on ph.sa_transacno = pd.sa_transacno    
--INNER JOIN Customer ON ph.sa_custno = Customer.Cust_code     
--INNER JOIN Item_SiteList ON pd.ItemSite_Code = Item_SiteList.ItemSite_Code     
--Where     
--pd.dt_deposit != 0 and pd.sa_date>=@FDate And pd.sa_date<=@TDate    
--And ((@Site='') OR ((@Site<>'') And pd.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
--And ((@staffCode='') OR ((@staffCode<>'') And ms.emp_code In (Select Item From dbo.LISTTABLE(@staffCode,',')))))   
--and pd.dt_deposit != 0 and pd.sa_date>=@FDate And pd.sa_date<=@TDate     
SELECT   distinct SS.sa_transacno,SS.item_code,     
(SELECT ' ' +isnull(US.Group_Desc,'PRIMARY')+' ' +US.emp_name+'-'+ convert(varchar, US.ratio)+'.'    
FROM #a1 US    
WHERE US.sa_transacno = SS.sa_transacno and US.item_code = SS.item_code    
FOR XML PATH('')) [sharedStaff] into #a2    
FROM #a1 SS    
GROUP BY SS.sa_transacno,SS.item_code    
ORDER BY 1    
    
Select X.dt_no,X.sa_transacno,X.dt_lineno,X.dt_itemno,X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],    
    
--STRING_SPLIT (X.payTypes,',') [payTypes],    
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],    
X.payTypes [payTypes],    
(case when X.[Group]='GT1' then 'Sales' else 'Non-Sales' end) as SalesGroup,    
X.ItemSite_Code [siteCode],    
X.ItemSite_Desc [siteName],    
sa_staffno,sa_staffname,    
isnull(sharedStaff,'') as sharedStaff,    
--(case when X.[Group]='GT1' then isnull(SUM(X.amt),0) else 0 end) as [amt],    
Convert(Decimal(19,2),isnull(SUM(X.Ratio),0)) [Ratio],    
isnull(SUM(X.payCN),0) [payCN],    
isnull(SUM(X.payContra),0) [payContra],    
isnull(SUM(X.grossAmt),0) [grossAmt],    
isnull(MAX(X.taxes),0) [taxes],    
isnull(SUM(X.gstRate),0) [gstRate],    
isnull(SUM(X.netAmt),0) [netAmt],    
isnull(SUM(X.BankCharges),0) [BankCharges],    
isnull(SUM(X.comm),0) [comm],    
isnull(SUM(X.amt),0) - ( isnull(SUM(X.amt),0) * isnull(SUM(X.BankCharges),0))/ 100 as [amt],    
isnull(SUM(X.amt),0) - ( isnull(SUM(X.amt),0) * isnull(SUM(X.BankCharges),0))/ 100 as total,    
isnull(SUM(X.amt),0) [amt1],    
isnull(SUM(X.total),0) total1      
--(case when X.[Group]='GT1' then isnull(SUM(X.total),0) else 0 end) as total    
from (    
select distinct pd.dt_no,pd.sa_transacno,pd.dt_lineno,pd.dt_itemno,    
employee.emp_code  as sa_staffno,    
employee.emp_name  as sa_staffname,    
--ph.sa_staffno,ph.sa_staffname,    
#a2.sharedStaff,    
convert (varchar,ph.sa_date,103)[payDate],     
Customer.Cust_name [customer],      
ph.SA_TransacNo_Ref [invoiceRef],     
ph.sa_transacno [payRef],Customer.Cust_Refer [CustRef],    
--pos_taud.pay_Desc [payTypes],    
pd.dt_itemdesc as [payTypes],    
--pos_taud.pay_actamt  [amt] ,     
0 [payContra],    
paytable.GT_Group [Group],    
--'' as [Group],    
--Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],    
0 as [payCN],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],    
0 as [grossAmt],    
--pos_taud.PAY_GST [taxes],    
0 as [taxes],    
--Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],    
0 as [gstRate],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],    
0 as [netAmt],    
0 [comm],    
--sum(isnull(bank_charges,0)) [BankCharges],    
0 as [BankCharges],    
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - isnull(bank_charges,0)+0 [total],    
pd.ItemSite_Code,Item_SiteList.ItemSite_Desc,    
--round(((pd.dt_deposit/100*ms.ratio)),2) amt ,round(((pd.dt_deposit/100*ms.ratio)),2) [total],    
round(pd.dt_deposit,2) as amt,round(pd.dt_deposit,2) as [total],    
ms.ratio    
FROM pos_daud pd    
inner join multistaff ms on ms.sa_transacno = pd.sa_transacno and pd.dt_lineno = ms.dt_lineno    
inner join employee on ms.emp_code = employee.emp_code    
inner join pos_haud ph on ph.sa_transacno = pd.sa_transacno    
INNER JOIN pos_taud ON ph.sa_transacno = pos_taud.sa_transacno    
INNER JOIN Customer ON ph.sa_custno = Customer.Cust_code     
INNER JOIN Item_SiteList ON pd.ItemSite_Code = Item_SiteList.ItemSite_Code     
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE    
left join #a2 on pd.sa_transacno=#a2.sa_transacNo and pd.dt_itemno=#a2.Item_Code    
Where     
--pd.sa_transacno='TCTPT7100091' and    
ph.isvoid = 0     
and paytable.gt_group = 'GT1'and    
pd.dt_deposit != 0     
and pd.sa_date>=@FDate And pd.sa_date<=@TDate    
And ((@Site='') OR ((@Site<>'') And pd.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
And ((@staffCode='') OR ((@staffCode<>'') And ms.emp_code In 
(Select Item From dbo.LISTTABLE(@staffCode,',')))) --pay    
group by pd.dt_no,pd.sa_transacno,pd.dt_lineno,pd.dt_itemno,employee.emp_code,
employee.emp_name,ph.sa_date,Customer.Cust_name,ph.SA_TransacNo_Ref,ph.sa_transacno,    
Customer.Cust_Refer,pd.dt_itemdesc,paytable.GT_Group,pd.ItemSite_Code,Item_SiteList.ItemSite_Desc,
pd.dt_deposit,ms.ratio,#a2.sharedStaff    
)X    
Group By X.dt_no,X.sa_transacno,X.dt_lineno,X.dt_itemno,X.payDate,X.customer,
X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,sa_staffno,sa_staffname,sharedStaff,[payRef],[CustRef],X.[Group]    
order by X.payDate,X.invoiceRef,X.dt_lineno    
  
  
----------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_Howmanycustomer')
BEGIN
DROP PROCEDURE Web_Howmanycustomer
END
GO 

CREATE  PROCEDURE Web_Howmanycustomer    
@FromDate varchar(20),    
@ToDate varchar(20),    
@Site varchar(max)    
AS    
Declare @FDate DATETIME            
Declare @TDate DATETIME            
 SET @FDate=Convert(Datetime,@FromDate,103)            
 SET @TDate=Convert(Datetime,@ToDate,103)            
select  Site_Code [Outlet],Cust_Code,Cust_name,isnull(Cust_Phone2,isnull(cust_phone1,'')) as Phone,    
case when (Cust_JoinDate is null) then  ''    
else    
Convert(varchar,Cust_JoinDate,106)     
end    
 [Join_Date],isnull(convert(numeric(10,2), TransRecord.Total),0) as Total    
   FROM Customer Left Outer JOIN      
(SELECT sa_custno, sum(sa_totamt) AS Total FROM pos_haud  GROUP BY sa_custno) TransRecord      
ON Customer.Cust_Code = TransRecord.sa_custno      
WHERE cust_joindate>= @FDate and cust_joindate <= @TDate and cust_isactive = '1'      
And ((@Site='') OR ((@Site<>'') And Site_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site        
ORDER BY Cust_JoinDate 



-----------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'webBI_RegularCustomerVisit')
BEGIN
DROP PROCEDURE webBI_RegularCustomerVisit
END
GO 

CREATE  PROCEDURE webBI_RegularCustomerVisit        
@FromDate varchar(20),        
@ToDate varchar(20), 
@FromTransDate varchar(20),        
@ToTransDate varchar(20), 
@Site varchar(max)        
AS        
Declare @FDate DATETIME                
Declare @TDate DATETIME                
Declare @FTDate DATETIME                
Declare @TTDate DATETIME                
 SET @FDate=Convert(Datetime,@FromDate,103)                
 SET @TDate=Convert(Datetime,@ToDate,103)                
 SET @FTDate=Convert(Datetime,@FromTransDate,103)                
 SET @TTDate=Convert(Datetime,@ToTransDate,103)                
select distinct c1.Site_Code [Outlet],c1.Cust_Code,c1.Cust_name,isnull(c1.Cust_Phone2,isnull(c1.cust_phone1,'')) as Phone,        
case when (c1.Cust_JoinDate is null) then  ''        
else        
Convert(varchar,c1.Cust_JoinDate,106)         
end        
 [Join_Date],
 isnull((select sum(sa_totamt) from pos_haud where pos_haud.sa_date>=@FTDate + '00:00:00.000' 
 and pos_haud.sa_date<=@TTDate + '23:59:59.999' 
 and  pos_haud.sa_custno=c1.cust_code group by sa_custno),0) as Total  
 from customer c1  
 left outer join   
   pos_haud   
 on c1.Cust_code=pos_haud.sa_custno  
 --where    (c1.cust_joindate> @FDate) and c1.cust_isactive = '1'          
  --where pos_haud.sa_custno not in (select cust_code from customer c2 where (c2.cust_joindate>= @FDate + '00:00:00.000' and c2.cust_joindate<= @TDate + '23:59:59.999' )) and c1.cust_isactive = '1'          
  where pos_haud.sa_custno not in (select cust_code from customer c2 where (c2.cust_joindate>= @FDate + '00:00:00.000')) 
and c1.cust_isactive = '1'          
And ((@Site='') OR ((@Site<>'') And c1.Site_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site            
Go



--------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_CustLastvisit')
BEGIN
DROP PROCEDURE Web_CustLastvisit
END
GO   
  
CREATE   PROCEDURE Web_CustLastvisit  
 @ToDate Varchar(10),    
@Site nvarchar(max)  
AS  
Declare @TDate DATETime  
SET @TDate=Convert(Datetime,@ToDate,103)   
  
SELECT Site_Code[Outlet],OR_KEY, Cust_Code, Cust_name, isnull(Cust_Phone2,'') [Phone],  
 case when (LV.LastVisitDate is null) then  
''   
else  
convert(varchar, LV.LastVisitDate , 106)  
end  
[Last_Date],  
 case when (LV.LastVisitDate is null) then  
''   
else  
Datediff(day,LV.LastVisitDate,@TDate)  
end  
as [absent]  
 ---LV.Absent1 [absent]  
  FROM Customer Left Outer JOIN  
(SELECT sa_custno, MAX(sa_date) AS LastVisitDate FROM pos_haud where isvoid = 0 GROUP BY sa_custno) LV  
ON Customer.Cust_Code = LV.sa_custno  
WHERE LV.LastVisitDate <= @TDate and cust_isactive = '1'  
And ((@Site='') OR ((@Site<>'') And Site_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site      
ORDER BY LastVisitDate  


----------------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_CustLastvisit1')
BEGIN
DROP PROCEDURE Web_CustLastvisit1
END
GO 

CREATE PROCEDURE Web_CustLastvisit1
 @ToDate Varchar(10),  
@Site nvarchar(max)
AS
Declare @TDate DATETime
SET @TDate=Convert(Datetime,@ToDate,103) 

select distinct p1.ItemSite_Code [Outlet], p1.sa_custno [Cust_Code],p1.sa_custname [Cust_Name],isnull(c1.cust_phone2,'') [Phone],
isnull((select top 1 Convert(Date,p2.sa_date,103) from pos_haud p2 where p2.sa_custno=p1.sa_custno order by sa_date desc),'') [Last_Date],
Datediff(day,isnull((select top 1 p2.sa_date from pos_haud p2 where p2.sa_custno=p1.sa_custno order by sa_date desc),convert(Date,getdate(),103)),@TDate) [absent]
 from pos_haud p1,customer c1
 where c1.cust_code=p1.sa_custno
 And ((@Site='') OR ((@Site<>'') And p1.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
 order by last_date desc
GO 




----------------


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'webBI_CustomerNewJoin')
BEGIN
DROP PROCEDURE webBI_CustomerNewJoin
END
GO
    
CREATE   PROCEDURE webBI_CustomerNewJoin  
 @Month Varchar(10),    
 @Year  Varchar(10),    
@Site nvarchar(max)  
AS  
SELECT Site_Code [Outlet], Cust_Code, Cust_name, isnull(Cust_Phone2,'') [Phone],   
case when (cust_joindate is null) then  
''   
else  
convert(varchar, cust_joindate, 106)  
  
end  
as [Join_Date],   
case when (TransRecord.FirstVisitDate is null) then  
''   
else  
convert(varchar, TransRecord.FirstVisitDate, 106)  
end  
as [First_Visit_Date],  
case when (TransRecord.LastVisitDate is null) then  
''   
else  
convert(varchar, TransRecord.LastVisitDate, 106)  
end  
as [Last_Visit_Date]  
   
  FROM Customer Left Outer JOIN  
(SELECT sa_custno, Min(sa_date) AS FirstVisitDate, MAX(sa_date) AS LastVisitDate   
FROM pos_haud where isvoid = 0 GROUP BY sa_custno) TransRecord  
ON Customer.Cust_Code = TransRecord.sa_custno  
WHERE month(cust_joindate) = @Month and year(cust_joindate) = @Year and cust_isactive = '1'  
And ((@Site='') OR ((@Site<>'') And Site_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
ORDER BY LastVisitDate  


-----------



IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_UpcomingAppointment')
BEGIN
DROP PROCEDURE Web_UpcomingAppointment
END
GO

CREATE  PROCEDURE Web_UpcomingAppointment  
 @FromDate nvarchar(10),  
 @ToDate nvarchar(10),  
 @Staff nvarchar(Max),  
 @Site nvarchar(Max)  
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103) 
select ItemSite_Code [Outlet],convert(varchar,appt_date,106) Appoint_Date,FORMAT(CAST(Appt_fr_time AS datetime), 'hh:mm tt') 'Fr_time',
FORMAT(CAST(Appt_to_time AS datetime), 'hh:mm tt') 'To_time',Cust_name,Appt_Phone,emp_name,Appt_remark from appointment
 where appt_isactive=1 and appt_status='Booking' 
 And convert(datetime,convert(varchar,appt_date,103),103)>=@FDate And convert(datetime,convert(varchar,appt_date,103),103)<=@TDate   
 And ((@Site='') OR ((@Site<>'') And ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
 And ((@Staff='') OR ((@Staff<>'') And emp_no In (Select Item From dbo.LISTTABLE(@Staff,',')))) --Staff
 order by appt_date
 Go


-----------



IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_MissedAppointment')
BEGIN
DROP PROCEDURE Web_MissedAppointment
END
GO
  
CREATE   PROCEDURE Web_MissedAppointment
 @FromDate nvarchar(10),    
 @Staff nvarchar(Max),    
 @Site nvarchar(Max)    
AS    
Declare @FDate DATE    
  
SET @FDate=Convert(Date,@FromDate,103)    
  
select ItemSite_Code [Outlet],isnull(convert(varchar,appt_date,106),'') Appoint_Date,isnull(FORMAT(CAST(Appt_fr_time AS datetime), 'hh:mm tt'),'') 'Fr_time',
isnull(FORMAT(CAST(Appt_to_time AS datetime), 'hh:mm tt'),'') 'To_time',  
isnull(Cust_name,'') Cust_name,isnull(Appt_Phone,'') Appt_Phone,isnull(emp_name,'') emp_name,isnull(Appt_remark,'') Appt_remark,  
case   
when (appt_Status='Cancelled') then  
'Cancelled'  
when (appt_status='Booking' and convert(date,Appt_date)<@FDate) then  
'Missed'  
end as [Status]  
 from appointment  
 where appt_isactive=1 and (appt_status='Cancelled' or (appt_status='Booking' and convert(date,Appt_Date)<@FDate))  
 And convert(date,Appt_Date)<@FDate  
 And ((@Site='') OR ((@Site<>'') And ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site    
 And ((@Staff='') OR ((@Staff<>'') And emp_no In (Select Item From dbo.LISTTABLE(@Staff,',')))) --Staff  
 order by ItemSite_Code,emp_name,appt_date  
GO


-------------
    
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'paydescription')
BEGIN
DROP PROCEDURE paydescription
END
GO      
create    procedure paydescription    
@PayGroup varchar(max),   
@PayGroup1 varchar(max)  
as    
if (@PayGroup1='GT1')  
 begin   
 select  pay_description from paytable where gt_group='GT1' and pay_isactive=1  
 And ((@PayGroup='') OR((@PayGroup<>'') And pay_code In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup     
 order by pay_code    
 end  
else if (@PayGroup1='GT2')  
 begin  
  select  pay_description from paytable where gt_group='GT2' and pay_isactive=1  
 And ((@PayGroup='') OR((@PayGroup<>'') And pay_code In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup     
 order by pay_code    
 end  
else  
 begin  
  select  pay_description from paytable where  pay_isactive=1  
 And ((@PayGroup='') OR((@PayGroup<>'') And pay_code In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup     
 order by pay_code    
 end  

-------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'paydescriptionns')
BEGIN
DROP PROCEDURE paydescriptionns
END
GO  

create  procedure paydescriptionns
@PayGroup varchar(max),
@PayGroup1 varchar(max)
as
select  pay_description from paytable  where pay_isactive=1 
And ((@PayGroup='') OR((@PayGroup<>'') And pay_code In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup   
order by gt_group,pay_code
go

----------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionExcelReport')
BEGIN
DROP PROCEDURE Web_DailyCollectionExcelReport
END
GO      
CREATE    PROCEDURE Web_DailyCollectionExcelReport
 @FromDate nvarchar(10),                  
 @ToDate nvarchar(10),                  
 @PayGroup nvarchar(Max),                  
 @PayGroup1 nvarchar(Max),     
 @Site nvarchar(Max)                  
AS                  
Declare @FDate DATETIME                  
Declare @TDate DATETIME                  
SET @FDate=Convert(Datetime,@FromDate,103)                  
SET @TDate=Convert(Datetime,@ToDate,103)                  
SELECT             
(select distinct Itemsite_Desc from item_sitelist where itemSite_Code=pos_haud.ItemSite_Code) [Outlet],                  
pos_haud.ItemSite_Code [site1],        
paytable.gt_group [PayGroup],            
pos_taud.pay_Desc [payTypes],                  
Convert(nvarchar,pos_haud.sa_date,103) [payDate],  
         
sum(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then             
(pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else             
pos_taud.PAY_GST End) - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE 
When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0            
 Else pos_taud.PAY_GST End) )/100  +0 , 3)) [beforeGST],                  
            
sum(Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then             
pos_taud.PAY_GST else (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else             
pos_taud.PAY_GST End) end)) [GST],                  
            
sum(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then             
(pos_taud.pay_actamt) Else 0 End ))   [afterGST]                 
             
FROM pos_haud INNER JOIN                  
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno                   
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code                   
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE                  
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo                  
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And 
convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate                   
and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )  
and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0                  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site                  
And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup               
group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group            
order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc 

------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionExcelReport1')
BEGIN
DROP PROCEDURE Web_DailyCollectionExcelReport1
END
GO 
      
CREATE     PROCEDURE Web_DailyCollectionExcelReport1
 @FromDate nvarchar(10),              
 @ToDate nvarchar(10),              
 @PayGroup nvarchar(Max),              
 @PayGroup1 nvarchar(Max),   
 @Site nvarchar(Max)              
AS              
Declare @FDate DATETIME              
Declare @TDate DATETIME              
SET @FDate=Convert(Datetime,@FromDate,103)              
SET @TDate=Convert(Datetime,@ToDate,103)              
SELECT         
(select distinct Itemsite_Desc from item_sitelist where itemSite_Code=pos_haud.ItemSite_Code) [Outlet],              
pos_haud.ItemSite_Code [site1],              
paytable.gt_group [PayGroup],        
pos_taud.pay_Desc [payTypes],              
Convert(nvarchar,pos_haud.sa_date,103) [payDate],      
           
sum(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then         
(pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else         
pos_taud.PAY_GST End) - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0        
 Else pos_taud.PAY_GST End) )/100  +0 , 3)) [beforeGST],              
        
sum(Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then         
pos_taud.PAY_GST else (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else         
pos_taud.PAY_GST End) end)) [GST],              
        
sum(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then         
(pos_taud.pay_actamt) Else 0 End ))   [afterGST]             
         
FROM pos_haud INNER JOIN              
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno               
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code               
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE              
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo              
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate 
And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate               
and paytable.pay_code in (select pay_code from paytable)  and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0              
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site              
And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup           
group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group        
order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc 


----------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_DailyCollectionExcelReport2')
BEGIN
DROP PROCEDURE Web_DailyCollectionExcelReport2
END
GO           
CREATE  PROCEDURE Web_DailyCollectionExcelReport2              
 @FromDate nvarchar(10),              
 @ToDate nvarchar(10),              
 @PayGroup nvarchar(Max),              
 @PayGroup1 nvarchar(Max),  
 @Site nvarchar(Max)              
AS              
Declare @FDate DATETIME              
Declare @TDate DATETIME              
SET @FDate=Convert(Datetime,@FromDate,103)              
SET @TDate=Convert(Datetime,@ToDate,103)              
SELECT         
(select distinct Itemsite_Desc from item_sitelist where itemSite_Code=pos_haud.ItemSite_Code) [Outlet],              
pos_haud.ItemSite_Code [site1],               
paytable.gt_group [PayGroup],        
pos_taud.pay_Desc [payTypes],              
Convert(nvarchar,pos_haud.sa_date,103) [payDate],              
pos_haud.SA_TransacNo_Ref [InvoiceNo],              
pos_haud.sa_custname [sa_custname],              
           
sum(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then         
(pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else         
pos_taud.PAY_GST End) - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0        
 Else pos_taud.PAY_GST End) )/100  +0 , 3)) [beforeGST],              
        
sum(Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then         
pos_taud.PAY_GST else (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else         
pos_taud.PAY_GST End) end)) [GST],              
        
sum(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then         
(pos_taud.pay_actamt) Else 0 End ))   [afterGST]             
         
FROM pos_haud INNER JOIN              
pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno               
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code               
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE              
Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo              
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate               
and paytable.pay_code in (select pay_code from paytable)  and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0              
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site              
And ((@PayGroup='') OR((@PayGroup<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayGroup,','))))--PayGroup           
group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group,pos_haud.SA_TransacNo_Ref,pos_haud.sa_custname        
order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc 



-----------
----For midyson
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SalesByCategory')
BEGIN
DROP PROCEDURE Web_SalesByCategory
END
GO     
CREATE  PROCEDURE Web_SalesByCategory
 @FromDate nvarchar(10),        
 @ToDate nvarchar(10),        
 @Site nvarchar(Max),        
 @Dept nvarchar(Max),        
 @GroupByStaff  nvarchar(1),        
 @ShowNonSales nvarchar(1),        
 @ShowOldBill nvarchar(1),        
 @ReportType nVarchar(10)        

AS        
Declare @FDate DATETIME        
Declare @TDate DATETIME        
SET @FDate=Convert(Datetime,@FromDate,103)        
SET @TDate=Convert(Datetime,@ToDate,103)
select Sales_Record.* , ISNULL(Item_Dept.itm_Desc,'') as Dept, 
case when Ttl_actamt.Ttl_actamt = 0 then
0
else
isnull((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit) ,0)
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

Where sadate>=@FDate +'00:00:00.000' And sadate<=@TDate + '23:59:59.999'
and IsVoid=0
and (Ttl_actamt.Ttl_actamt>0 and ((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0 or (GT2_actamt.GT2_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0))
and (@ShowOldBill='Y' OR (@ShowOldBill='N' AND (Pay_OldBill.OldBill_Count=0 or Pay_OldBill.OldBill_Count is null)))
And ((@Site='') OR ((@Site<>'') And Outlet In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site               
And ((@Dept='') OR ((@Dept<>'') And Item_Dept.itm_Desc In (Select Item From dbo.LISTTABLE(@Dept,','))))--Department        
ORDER BY SA_TRANSACNO
----For midyson




-----------

----------


----For midyson
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_SalesByClass')
BEGIN
DROP PROCEDURE Web_SalesByClass
END
GO  
CREATE  PROCEDURE Web_SalesByClass
 @FromDate nvarchar(10),        
 @ToDate nvarchar(10),        
 @Site nvarchar(Max),        
 @Dept nvarchar(Max),        
 @GroupByStaff  nvarchar(1),        
 @ShowNonSales nvarchar(1),        
 @ShowOldBill nvarchar(1),        
 @ReportType nVarchar(10)        

AS        
Declare @FDate DATETIME        
Declare @TDate DATETIME        
SET @FDate=Convert(Datetime,@FromDate,103)        
SET @TDate=Convert(Datetime,@ToDate,103)
select Sales_Record.* , ISNULL(Item_Class.itm_Desc,'') as Class, 
case when Ttl_actamt.Ttl_actamt = 0 then
0
else
isnull((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit) ,0)
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

LEFT OUTER JOIN Item_Class on Stock.Item_Class = Item_Class.itm_Code

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

Where sadate>=@FDate +'00:00:00.000' And sadate<=@TDate + '23:59:59.999'
and IsVoid=0
and (Ttl_actamt.Ttl_actamt>0 and ((GT1_actamt.GT1_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0 or (GT2_actamt.GT2_ActAmt / Ttl_actamt.Ttl_actamt * Sales_Record.dt_deposit)>0))
and (@ShowOldBill='Y' OR (@ShowOldBill='N' AND (Pay_OldBill.OldBill_Count=0 or Pay_OldBill.OldBill_Count is null)))
And ((@Site='') OR ((@Site<>'') And Outlet In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site               
And ((@Dept='') OR ((@Dept<>'') And Item_Class.itm_Desc In (Select Item From dbo.LISTTABLE(@Dept,','))))--Department        
ORDER BY SA_TRANSACNO
----For midyson


----------
------------
IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_Reporttittlesite')
BEGIN
DROP PROCEDURE Web_Reporttittlesite
END
GO  
create  procedure Web_Reporttittlesite
@siteCode nvarchar(30)
as
select Top 1 Title,Comp_Title1,Comp_Title2,Comp_Title3,Comp_Title4,Footer_1,Footer_2,Footer_3,Footer_4 from Title where product_license=@siteCode
go


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_Reporttittle')
BEGIN
DROP PROCEDURE Web_Reporttittle
END
GO  
create  procedure Web_Reporttittle  
as  
select Top 1 Title,Comp_Title1,Comp_Title2,Comp_Title3,Comp_Title4,Footer_1,Footer_2,Footer_3,Footer_4 from Title   
go


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_ReporttittleHQ')
BEGIN
DROP PROCEDURE Web_ReporttittleHQ
END
GO  
create  procedure Web_ReporttittleHQ  
as  
select Top 1 Title,Comp_Title1,Comp_Title2,Comp_Title3,Comp_Title4,Footer_1,Footer_2,Footer_3,Footer_4 from Title where product_license LIKE '%HQ%'  
go

-------------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'SP_COMM_REPORT_FOR_ALL_SITE')
BEGIN
DROP PROCEDURE SP_COMM_REPORT_FOR_ALL_SITE
END
GO 
CREATE   PROCEDURE SP_COMM_REPORT_FOR_ALL_SITE    
@FROMDATE NVARCHAR(50),    
@TODATE NVARCHAR(50)    
AS    
    
SELECT [EMP_CODE],DAY_DATE, max(VRSN_NO) as VRSN_NO into #temp1    
FROM[DAY_CMTN_RECORDES] D     
WHERE     
D.DAY_DATE BETWEEN convert(datetime,@FROMDATE, 103)  and convert(datetime,@TODATE, 103)      
group by [EMP_CODE],DAY_DATE    
    
    
SELECT siteCode,Item_SiteList.itemsite_desc,D.[EMP_CODE],Employee.[Emp_name],sum([COURSE_AMNT]) as courseAmnt,    
sum([COURSE_CMTN]) as courseComm,sum([RETAIL_AMNT]) as retailAmnt,sum([RETAIL_CMTN]) as retailComm ,    
sum([COURSE_AMNT])+ sum([RETAIL_AMNT]) as totalSales    ,    
sum([FST_TD_CMTN]) + sum([COURSE_CMTN]) + sum([RETAIL_CMTN] )  as totalComm ,    
sum(TD_CMTN) as TDComm,sum(TD_AMNT) as TDAmnt,    
round(isnull(NULLIF(sum(TD_CMTN),0) /NULLIF(sum(TD_AMNT),0),0) * 100 ,2) as ServicePerc,  
'' as FIXED,  
sum([COURSE_CMTN])+sum([RETAIL_CMTN])+sum(TD_CMTN)+ sum([COURSE_AMNT])+ sum([RETAIL_AMNT]) + round(isnull(NULLIF(sum(TD_CMTN),0) /NULLIF(sum(TD_AMNT),0),0) * 100 ,2) as total  
FROM[DAY_CMTN_RECORDES] D      
left join Employee on D.EMP_CODE=Employee.Emp_code      
left join Item_SiteList on D.siteCode=Item_SiteList.itemsite_code       
inner join #temp1 B on D.DAY_DATE=B.DAY_DATE and D.[EMP_CODE]=B.[EMP_CODE] and D.VRSN_NO=B.VRSN_NO    
WHERE     
D.DAY_DATE BETWEEN convert(datetime,@FROMDATE, 103)  and convert(datetime,@TODATE, 103)     
group by siteCode,Item_SiteList.itemsite_desc,D.[EMP_CODE],Employee.[Emp_name]      
order by siteCode    
    
drop table #temp1 

---------



IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'webBI_SummaryStaffwise')
BEGIN
DROP PROCEDURE webBI_SummaryStaffwise
END
GO 

CREATE PROCEDURE webBI_SummaryStaffwise
@FromDate nvarchar(50),        
 @ToDate nvarchar(50),        
 @Site nvarchar(Max),
 @Staff nvarchar(max)

AS  

Declare @FDate Datetime                       
Declare @TDate Datetime                      
SET @FDate=Convert(Datetime,@FromDate,103)                          
SET @TDate=Convert(Datetime,@ToDate,103)   

select  ap1.ItemSite_Code,ap1.emp_name,
--BETWEEN convert(datetime,@FROMDATE, 103)  and convert(datetime,@TODATE, 103)
(select count(*) from appointment where appt_status='Done' and appt_date>=@FDate and appt_date<=@TDate and emp_name=ap1.emp_name) as [Totdone] ,
(select count(*) from appointment where appt_status='Cancelled' and  appt_date>=@FDate and appt_date<=@TDate  and emp_name=ap1.emp_name) as [totcancelled],
(select count(*) from appointment where appt_status='Late' and  appt_date>=@FDate and appt_date<=@TDate  and emp_name=ap1.emp_name) as [totLate],
(select count(*) from appointment where appt_status='Waiting' and  appt_date>=@FDate and appt_date<=@TDate  and emp_name=ap1.emp_name) as [totWaiting],
(select count(*) from appointment where appt_status='Booking' and  appt_date>=@FDate and appt_date<=@TDate  and emp_name=ap1.emp_name) as [totBooking],
(select  convert(char(8),dateadd(second,SUM ( DATEPART(hh,(convert(datetime,(convert(varchar,convert(time,convert(datetime,appt_to_time)-convert(datetime,appt_fr_time)),108)),1))) * 3600 +
DATEPART(mi, (convert(datetime,(convert(varchar,convert(time,convert(datetime,appt_to_time)-convert(datetime,appt_fr_time)),108)),1))) * 60 + DATEPART(ss,(convert(datetime,(convert(varchar,convert(time,convert(datetime,appt_to_time)-convert(datetime,appt_fr_time)),108)),1)))),0),108)
 from appointment where  emp_name=ap1.emp_name and appt_status='Done' and  appt_date>=@FDate and appt_date<=@TDate ) as [hrs1] 
-- (select sum(sa_totamt) from pos_haud where sa_staffname=ap1.emp_name  and sa_date>=@FDate + ' 00:00:00' and appt_date<=@TDate + ' 23:59:59') as [totsales]
  
into ##TEMP_2 
from appointment ap1  
where 
((@Site='') OR ((@Site<>'') And ap1.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
And ((@Staff='') OR ((@Staff<>'') And ap1.emp_name In (Select Item From dbo.LISTTABLE(@Staff,',')))) --Site 
select distinct ItemSite_Code [Outlet],emp_name,Totdone,totcancelled,totLate,totWaiting,totBooking,isnull(hrs1,0) as Totalworked from ##TEMP_2 where ([Totdone]>0 or [totcancelled]>0) 
DROP TABLE ##TEMP_2 
Go
 

--------


IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_AppointmentHistory')
BEGIN
DROP PROCEDURE Web_AppointmentHistory
END
GO 
CREATE  PROCEDURE Web_AppointmentHistory
 @FromDate nvarchar(10),  
 @ToDate nvarchar(10),  
 @Staff nvarchar(Max),  
 @Site nvarchar(Max),
 @Status nvarchar(Max)
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103) 
SELECT ItemSite_Code [Outlet],emp_name,
case when appt_status = 'Done' then
  'Done'
when isArrive=1 then
 'Arrived'
when isLate=1 then
  'Late Arrival' 
when Appt_cancel=1 then
  'Cancelled'
when Appt_Comfirm=1 then
  'Confirm'
when Booking=1 then
  'Booking'
when Waiting=1 then
 'Waiting'
 when appt_status='Waiting' then
 'Waiting'
 end
 as app_status,

convert(date,appt_date,106) Appoint_Date, FORMAT(CAST(Appt_fr_time AS datetime), 'hh:mm tt') 'Fr_time',FORMAT(CAST(Appt_to_time AS datetime), 'hh:mm tt') 'To_time', cust_no, ISNULL(cust_refer, '') As [Cust_Refer], cust_name, Appt_Remark, Convert(int,requestTherapist ) as requestTherapist
into ##TEMP_2
FROM Appointment 
 where convert(datetime,convert(varchar,appt_date,103),103)>=@FDate And convert(datetime,convert(varchar,appt_date,103),103)<=@TDate   
 And Cust_No <> ''
 And ((@Site='') OR ((@Site<>'') And ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
 And ((@Staff='') OR ((@Staff<>'') And emp_no In (Select Item From dbo.LISTTABLE(@Staff,',')))) --Staff
 order by appt_date,Appt_Fr_time
 
 select * from ##TEMP_2 
 where ((@Status='') OR ((@Status<>'') And app_status In (Select Item From dbo.LISTTABLE(@Status,',')))) --Staff 
order by outlet,emp_name,Appoint_Date
 
 DROP TABLE ##TEMP_2 
 Go

------

IF EXISTS(SELECT * FROM sys.procedures WHERE NAME LIKE 'Web_CustomerReferral')
BEGIN
DROP PROCEDURE Web_CustomerReferral
END
GO
CREATE  PROCEDURE Web_CustomerReferral
 @FromDate nvarchar(10),  
 @ToDate nvarchar(10),  
 @Site nvarchar(Max)
AS  
Declare @FDate DATETIME  
Declare @TDate DATETIME  
SET @FDate=Convert(Datetime,@FromDate,103)  
SET @TDate=Convert(Datetime,@ToDate,103)
select (Select ItemSite_Desc from Item_SiteList where ItemSite_Code=c1.Site_Code) [Outlet],c1.cust_code [Cust_Code],Convert(date,c1.Cust_JoinDate,103) [Cust_JoinDate],c1.Cust_name [Cust_Name],
(Select count(*) from Customer where (cust_refer is not null and cust_refer <> '') and cust_code=c1.cust_code) as TotRefer 
from Customer c1
Where c1.Cust_JoinDate>=@FDate +'00:00:00' And c1.Cust_JoinDate<=@TDate + '23:59:59'
And ((@Site='') OR ((@Site<>'') And Site_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site 
Order by TotRefer desc, c1.cust_code 

---------



select top 1000 p.objid, s.class, u,g,r,i,p.z, p.specObjID, dbo.fGetUrlFitsSpectrum(p.specObjID) as spectrum into mydb.MyTable_5 from PhotoObjAll p join SpecObjAll s on p.specObjID=s.specObjID
where p.specObjID is not null
and p.specObjID!=0
  and p.u between 19 and 20
  and clean = 1 and (calibStatus_r & 1) != 0
and s.class='QSO'

cut -f9 -d',' star_orig.csv > star_spectra_links

select count(*)
from Users as U
where CountryCode is null
or CountryCode = ''  

select count(*)
from Users as U
where CountryCode is not null 
and CountryCode <> ''


select count(distinct U.Id)
from Users as U
join DeviceClients as DC on U.Id = DC.UserId
where U.CountryCode is null 
and DC.CountryCode is not null
and DC.CountryCode <> ''
option(maxdop 3)   


select U.Id as UserID , U.CountryCode
from Users as U
where CountryCode is not null 
and CountryCode <> ''
and CountryCode <> '***'

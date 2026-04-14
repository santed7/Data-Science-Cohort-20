# Ames Housing Dataset — Data Dictionary

**Source:** De Cock, D. (2011). *Ames, Iowa: Alternative to the Boston Housing Data Set.* Journal of Statistics Education, 19(3).  
**Size:** 2,930 observations, 82 variables (23 nominal, 23 ordinal, 14 discrete, 20 continuous + 2 identifiers)  
**Task:** Predict `SalePrice` using regression

---

## Target Variable

| Variable | Type | Description |
|----------|------|-------------|
| `SalePrice` | Continuous | Sale price in dollars — the variable to predict |

---

## Identification

| Variable | Type | Description |
|----------|------|-------------|
| `Order` | Discrete | Observation number |
| `PID` | Nominal | Parcel identification number |
| `MSSubClass` | Nominal | Building class / type of dwelling (20=1-story 1946+, 30=1-story 1945-, 60=2-story 1946+, 70=2-story 1945-, 80=Split/Multi-level, 85=Split Foyer, 90=Duplex, 120=1-story PUD, 160=2-story PUD, 190=2-family conversion) |
| `MSZoning` | Nominal | General zoning classification (A=Agriculture, C=Commercial, FV=Floating Village, I=Industrial, RH=Res. High Density, RL=Res. Low Density, RM=Res. Medium Density) |

---

## Lot

| Variable | Type | Description |
|----------|------|-------------|
| `LotFrontage` | Continuous | Linear feet of street connected to property |
| `LotArea` | Continuous | Lot size in square feet |
| `Street` | Nominal | Road access type (Grvl=Gravel, Pave=Paved) |
| `Alley` | Nominal | Alley access type (Grvl, Pave, NA=No alley access) |
| `LotShape` | Ordinal | General shape (Reg=Regular, IR1=Slightly irregular, IR2=Moderately irregular, IR3=Irregular) |
| `LandContour` | Nominal | Flatness (Lvl=Near flat, Bnk=Banked, HLS=Hillside, Low=Depression) |
| `Utilities` | Ordinal | Utilities available (AllPub=All public, NoSewr=No sewer, NoSeWa=No sewer/water, ELO=Electricity only) |
| `LotConfig` | Nominal | Lot configuration (Inside, Corner, CulDSac, FR2=Frontage on 2 sides, FR3=Frontage on 3 sides) |
| `LandSlope` | Ordinal | Slope (Gtl=Gentle, Mod=Moderate, Sev=Severe) |

---

## Location

| Variable | Type | Description |
|----------|------|-------------|
| `Neighborhood` | Nominal | Physical location within Ames city limits (28 neighborhoods: Blmngtn, Blueste, BrDale, BrkSide, ClearCr, CollgCr, Crawfor, Edwards, Gilbert, Greens, GrnHill, IDOTRR, Landmrk, MeadowV, Mitchel, Names, NoRidge, NPkVill, NridgHt, NWAmes, OldTown, SWISU, Sawyer, SawyerW, Somerst, StoneBr, Timber, Veenker) |
| `Condition1` | Nominal | Proximity to conditions (Norm, Artery=Arterial street, Feedr=Feeder street, RRNn/RRAn=N-S Railroad, RRNe/RRAe=E-W Railroad, PosN=Near park/greenbelt, PosA=Adjacent to positive feature) |
| `Condition2` | Nominal | Second proximity condition if more than one present (same codes as Condition1) |

---

## Structure

| Variable | Type | Description |
|----------|------|-------------|
| `BldgType` | Nominal | Type of dwelling (1Fam=Single family, 2FmCon=2-family conversion, Duplx=Duplex, TwnhsE=Townhouse End unit, TwnhsI=Townhouse Inside unit) |
| `HouseStyle` | Nominal | Style of dwelling (1Story, 1.5Fin, 1.5Unf, 2Story, 2.5Fin, 2.5Unf, SFoyer=Split Foyer, SLvl=Split Level) |
| `OverallQual` | Ordinal | Overall material and finish quality (1=Very Poor to 10=Very Excellent) |
| `OverallCond` | Ordinal | Overall condition rating (1=Very Poor to 10=Very Excellent) |
| `YearBuilt` | Discrete | Original construction year |
| `YearRemodAdd` | Discrete | Remodel date (same as YearBuilt if no remodel or additions) |
| `RoofStyle` | Nominal | Roof type (Flat, Gable, Gambrel, Hip, Mansard, Shed) |
| `RoofMatl` | Nominal | Roof material (ClyTile, CompShg=Composite Shingle, Membran, Metal, Roll, Tar&Grv=Gravel & Tar, WdShake, WdShngl) |
| `Exterior1st` | Nominal | Primary exterior covering (AsbShng, AsphShn, BrkComm, BrkFace, CBlock, CemntBd, HdBoard, ImStucc, MetalSd, Plywood, Stone, Stucco, VinylSd, Wd Sdng, WdShing) |
| `Exterior2nd` | Nominal | Secondary exterior covering if more than one material (same codes as Exterior1st) |
| `MasVnrType` | Nominal | Masonry veneer type (BrkCmn, BrkFace, CBlock, None, Stone) |
| `MasVnrArea` | Continuous | Masonry veneer area in square feet |
| `ExterQual` | Ordinal | Exterior material quality (Ex=Excellent, Gd=Good, TA=Average, Fa=Fair, Po=Poor) |
| `ExterCond` | Ordinal | Exterior material current condition (Ex, Gd, TA, Fa, Po) |
| `Foundation` | Nominal | Foundation type (BrkTil=Brick & Tile, CBlock=Cinder Block, PConc=Poured Concrete, Slab, Stone, Wood) |

---

## Basement

| Variable | Type | Description |
|----------|------|-------------|
| `BsmtQual` | Ordinal | Basement height (Ex=100+ in, Gd=90–99 in, TA=80–89 in, Fa=70–79 in, Po=<70 in, NA=No Basement) |
| `BsmtCond` | Ordinal | General basement condition (Ex, Gd, TA=slight dampness OK, Fa=dampness/cracking, Po=severe cracking/wetness, NA) |
| `BsmtExposure` | Ordinal | Walkout or garden-level walls (Gd=Good, Av=Average, Mn=Minimum, No=None, NA) |
| `BsmtFinType1` | Ordinal | Basement finished area rating (GLQ=Good Living Quarters, ALQ, BLQ, Rec=Avg Rec Room, LwQ=Low Quality, Unf=Unfinished, NA) |
| `BsmtFinSF1` | Continuous | Type 1 finished basement square feet |
| `BsmtFinType2` | Ordinal | Rating of basement finished area if multiple types (same codes as BsmtFinType1) |
| `BsmtFinSF2` | Continuous | Type 2 finished basement square feet |
| `BsmtUnfSF` | Continuous | Unfinished basement square feet |
| `TotalBsmtSF` | Continuous | Total basement square feet |
| `BsmtFullBath` | Discrete | Full bathrooms in basement |
| `BsmtHalfBath` | Discrete | Half bathrooms in basement |

---

## Utilities & Systems

| Variable | Type | Description |
|----------|------|-------------|
| `Heating` | Nominal | Heating type (Floor, GasA=Gas forced warm air, GasW=Gas hot water/steam, Grav=Gravity furnace, OthW=Other hot water/steam, Wall=Wall furnace) |
| `HeatingQC` | Ordinal | Heating quality and condition (Ex, Gd, TA, Fa, Po) |
| `CentralAir` | Nominal | Central air conditioning (Y=Yes, N=No) |
| `Electrical` | Ordinal | Electrical system (SBrkr=Standard Circuit Breakers, FuseA=Fuse >60 AMP, FuseF=60 AMP Fuse, FuseP=60 AMP knob & tube, Mix) |

---

## Living Area

| Variable | Type | Description |
|----------|------|-------------|
| `1stFlrSF` | Continuous | First floor square feet |
| `2ndFlrSF` | Continuous | Second floor square feet |
| `LowQualFinSF` | Continuous | Low quality finished square feet (all floors) |
| `GrLivArea` | Continuous | Above-grade ground living area in square feet — typically the strongest numeric correlator with price |
| `FullBath` | Discrete | Full bathrooms above grade |
| `HalfBath` | Discrete | Half bathrooms above grade |
| `BedroomAbvGr` | Discrete | Bedrooms above grade (excludes basement bedrooms) |
| `KitchenAbvGr` | Discrete | Kitchens above grade |
| `KitchenQual` | Ordinal | Kitchen quality (Ex, Gd, TA, Fa, Po) |
| `TotRmsAbvGrd` | Discrete | Total rooms above grade (does not include bathrooms) |
| `Functional` | Ordinal | Home functionality (Typ=Typical, Min1/Min2=Minor deductions, Mod=Moderate, Maj1/Maj2=Major deductions, Sev=Severely damaged, Sal=Salvage only) |
| `Fireplaces` | Discrete | Number of fireplaces |
| `FireplaceQu` | Ordinal | Fireplace quality (Ex=Exceptional masonry, Gd=Masonry main level, TA=Prefab or basement masonry, Fa=Prefab basement, Po=Ben Franklin Stove, NA=No Fireplace) |

---

## Garage

| Variable | Type | Description |
|----------|------|-------------|
| `GarageType` | Nominal | Garage location (2Types=More than one type, Attchd=Attached, Basment=Basement, BuiltIn=Built-in, CarPort, Detchd=Detached, NA=No Garage) |
| `GarageYrBlt` | Discrete | Year garage was built |
| `GarageFinish` | Ordinal | Interior finish (Fin=Finished, RFn=Rough Finished, Unf=Unfinished, NA) |
| `GarageCars` | Discrete | Garage capacity in number of cars |
| `GarageArea` | Continuous | Garage size in square feet |
| `GarageQual` | Ordinal | Garage quality (Ex, Gd, TA, Fa, Po, NA) |
| `GarageCond` | Ordinal | Garage condition (Ex, Gd, TA, Fa, Po, NA) |
| `PavedDrive` | Ordinal | Paved driveway (Y=Paved, P=Partial Pavement, N=Dirt/Gravel) |

---

## Outdoor Features

| Variable | Type | Description |
|----------|------|-------------|
| `WoodDeckSF` | Continuous | Wood deck area in square feet |
| `OpenPorchSF` | Continuous | Open porch area in square feet |
| `EnclosedPorch` | Continuous | Enclosed porch area in square feet |
| `3SsnPorch` | Continuous | Three season porch area in square feet |
| `ScreenPorch` | Continuous | Screen porch area in square feet |
| `PoolArea` | Continuous | Pool area in square feet |
| `PoolQC` | Ordinal | Pool quality (Ex, Gd, TA, Fa, NA=No Pool) |
| `Fence` | Ordinal | Fence quality (GdPrv=Good Privacy, MnPrv=Min Privacy, GdWo=Good Wood, MnWw=Min Wood/Wire, NA=No Fence) |
| `MiscFeature` | Nominal | Miscellaneous feature (Elev=Elevator, Gar2=2nd Garage, Othr, Shed=Shed >100 SF, TenC=Tennis Court, NA=None) |
| `MiscVal` | Continuous | Dollar value of miscellaneous feature |

---

## Sale Information

| Variable | Type | Description |
|----------|------|-------------|
| `MoSold` | Discrete | Month sold (1–12) |
| `YrSold` | Discrete | Year sold (2006–2010) |
| `SaleType` | Nominal | Type of sale (WD=Warranty Deed conventional, CWD=Warranty Deed cash, VWD=Warranty Deed VA loan, New=New construction, COD=Court Officer Deed, Con=Contract 15% down, ConLw=Contract low down/interest, ConLI=Contract low interest, ConLD=Contract low down, Oth=Other) |
| `SaleCondition` | Nominal | Condition of sale (Normal, Abnorml=Trade/foreclosure/short sale, AdjLand=Adjoining land purchase, Alloca=Allocation/condo+garage, Family=Sale between family members, Partial=Home not completed at assessment) |

---

## Notes for Modeling

- **`NA` values in many categorical columns** (Alley, BsmtQual, FireplaceQu, GarageType, PoolQC, Fence, MiscFeature) mean "not present," not truly missing data — encode accordingly.
- **Outliers:** 5 observations with `GrLivArea` > 4,000 sq ft are unusual sales and are commonly removed before modeling.
- **Skewness:** `SalePrice` is right-skewed — consider log-transforming the target for regression.
- **High-value features** for prediction: `OverallQual`, `GrLivArea`, `GarageCars`, `GarageArea`, `TotalBsmtSF`, `1stFlrSF`, `FullBath`, `TotRmsAbvGrd`, `YearBuilt`, `YearRemodAdd`.

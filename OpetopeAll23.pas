{Opetopes, Top Hamiltonian Path, Sign}

{Places to put parameters:
1. dim - dimension of the multitope
2. n - number of faces in the multitope
3. file with the graph of incidence of facess (codomain first)
   the graph must come from a multitope (Now: positive only)
4. file with translation of numbers of face to other names

Other comments:
5. For for alphanumeric presentation of faces put (j>dim) condition
   in procedute write_walk (and in write_walk1 test) procedure
6. in file gg.txt is file with the graph as entered
7. in file walk_file is the file with the ordered (if possible)
   set of different columns, with the check if it is correct
8. File produced: walk_file,
9. File that could be produced: Other_files+'gg.txt' diff.txt
                                TestedPath.txt, Other_files+'flags_file.txt'
10. ... and now much more
11. integer changed to longint}


uses Crt;
const opetope_file='opetope3.txt';  {file with face structure of the opetope}
      max_dim=10;
      max_path=15000;   {maximal length of a Hamiltonian Path; default 1000}
      max_display=30;  {number of flags displayed in one line; default 20}
      max_faces=300;   {maximal number of faces in an opetope}
type
  {Types for Hamiltonian paths}
  Col=array[-3..max_dim+3] of longint; {for columns}
  Set_Col=array[-3..max_dim+3,1..max_path] of longint;
  Set_Col2=array[-3..max_dim+3,1..2*max_path] of longint;
  Orders=array[1..max_faces] of ^Set_Col;
  Face_Order=array[1..max_faces] of longint;
  Raw=array[1..max_path] of boolean;
  Dimension=array[0..max_faces] of longint;
  Names= array[0..max_faces] of string[3];
  {Types for list of faces in an opetope}
  Pt=^Node;
  Node=record
          id:longint;
          next : pt
       end;
  Graph= array [0..max_faces] of Pt;
  {Types for list of faces in the product I x P}
  List=^Elt;
  Elt=record
        co:Col;
        next:List
      end;
  ListPr=^FacePr;
  FacePr=record   {list of faces in the product}
              co : col; {col with a face in I x P}
              next : List;   {next face in theta}
              nextPr : ListPr
        end;

  {Types for opetope linked face structure}
  OpetopeList=^OpetopeFace;
  DomList=^DomFace;
  OpetopeFace=record
                face: longint;
                cod : OpetopeList;
                dom : DomList;
                codOf : DomList;
                domOf : DomList;
              end;
  DomFace=record
               FaceDom : OpetopeList;
               nextDom : DomList
             end;
  OpetopeTab=array[0..max_faces] of OpetopeList;

  {Types for relations on faces, e.g. relations}
  Face_rel = array[0..max_faces,0..max_faces] of boolean;

var
  top, dim, n, length: longint;
  {top - the number of the top face; dim - dimension of a multitop;
   n -  number of faces; length - length of the Hamiltonian path}
  face_dim,lengths:dimension;
  {face_dimension - keeps dimensions of faces in P;
   lengths - keeps lenghts of Hamiltonian paths of faces of P}
  translation,  walk_file, Other_files : string;
  {translation - file with alphanumeric (3 letters) translation;
   walk_file - file where the Hamiltonian path will be saved
   Other_files - like walk file but without .txt; this is for other files
                 produced by the program to have recognizable name }
  LI,LIall:graph;  {LI array of (heads) of lists keeping codomain followed
              by domains of faces;
              LIall array of (heads) of lists of all faces
              incident with the given one}
  List_col,List_col1,Walk_col,Walk_col1 : Set_Col;
  Walk_col2:Set_Col2;
  {List_col has all max flags found by DFS;
  List_col1 is List_col with first two column exchanged;
  Walk_col calculates walk starting from `gamma's of the top'
  i.e. from List_col;
  Walk_col1 calculates walk starting from `delata' of `gamma's of the top'
  i.e. from List_col1;}
  {color:array[-1..max_faces] of boolean;}
  {Koll:col;}
  Transl : Names;
  {Ord : Face_rel;} {for order on all faces}
  All_correct : boolean;
  ff : text;
  {Pointer to the list of list}
  Product, ProductLast: ListPr; {Product - pointer to the list of list
  with faces and their gamma's and delta's, ProductLast - on non-empty list
  it points to the last element on the list}
  Order : Orders; {array of pointers to arrays set_col
                   that will store top paths for all faces of P}
  TopFace : OpetopeList; {pointer to the top of the linked structure
                          storing the opetope}
  OpetopeArray : OpetopeTab;

  UpperRel, LowerRel, GlobalRel: Face_rel;
  Upper, Lower, Global : Face_order;
{SECTION: WRITE PROCEDURES}

procedure write_col(C:col; {x:longint;} var f:text);
{write column C : set_col  to the file}
 var i,j,k,a:longint;
begin
  {writeln(f,'Column ',x,':');}
      for i:=-3 to C[-3] do
        write(f,C[i]:4);
  writeln(f);
end;

procedure write_set_col(C:set_col;high,low,le,ri:longint; var f:text);
{write array C : set_col  to the file f
limits: high, low, le, ri}
 var i,j,k,a:longint;
begin
  writeln(f,'Number of flags: ',ri);
  for k:=0 to ((ri-1) div max_display) do  begin
  for j:=high downto low do
  // if (j<>high-1) and (j<>high-2) {(j=high) and (j=high-4)} then
  begin
      if (j=high-3) then begin
        for i:=1 to max_display do
          if (k<(ri div max_display)) or (i<=(ri mod max_display))
               then write(f,'   --');
        writeln(f);
      end;
      for i:=1 to max_display do begin
        a:=C[j,(k*max_display)+i];   //write(i:4);
        if (k<(ri div max_display)) or (i<=(ri mod max_display))
        then  write(f,a:5)
      end;
    writeln(f);

    end;
    writeln(f);
  end;
end;

procedure write_set_col2(C:set_col2;high,low,le,ri:longint; var f:text);
{write array C : set_col  to the file f
limits: high, low, le, ri}
 var i,j,k,a:longint;
begin
  writeln(f,'Number of flags and p-falgs: ',ri);
  for k:=0 to ((ri-1) div max_display) do  begin
  for j:=high downto low do begin
      if (j=high-1) then begin
        for i:=1 to max_display do
          if (k<(ri div max_display)) or (i<=(ri mod max_display))
               then write(f,'   --');
        writeln(f);
      end;
      for i:=1 to max_display do begin
        a:=C[j,(k*max_display)+i];
        if (k<(ri div max_display)) or (i<=(ri mod max_display))
        then  write(f,a:5)
      end;
    writeln(f);
  end;
    writeln(f);
  end;
end;

procedure write_set_col3(C:set_col2;high,low,le,ri:longint; var f:text);
{write array C : set_col  to the file f
limits: high, low, le, ri; only even flags, i.e. only p-flags}
 var i,j,k,a:longint;
begin
//writeln('ri, ri iv 2, (ri-1) div max_display: ',ri:4,ri div 2:4, (ri-1) div max_display : 4);
  writeln(f,'Number of p-falgs: ',ri div 2);
  for k:=0 to ((ri -2)  div max_display) do  begin  writeln(f,k:4);
  for j:=high downto low do begin
      if (j=high-1) then begin
        for i:=1 to max_display do
          {if (k<((ri div 2) div max_display)) or (i<=((ri div 2) mod max_display))
               then} write(f,'   --');
        writeln(f);
      end;
      for i:=1 to max_display do begin
        a:=C[j,(k*max_display)+2*i];
        {if (k<((ri div 2) div max_display)) or (i<=((ri div 2) mod max_display))
        then}  if j<>high then write(f,a:5) else write(f,a div 2 :5);
      end;
    writeln(f);
  end;
    writeln(f);
  end;
end;

procedure list_face_structure(var L:graph;s :string);
{lists read face_structure to the file Other_files+'Faces.txt'}
var u:pt;
    f:text;
    i:longint;
begin
assign(f,Other_files+s);
rewrite(f);
for i:=0 to n do begin
  write(f,i,' '); u:=L[i];
  while u<>nil do begin
    write(f,u^.id,' ');
    u:=u^.next
  end;
  writeln(f);
end;
{writeln(f);
writeln(f,'Alphanumeric: ');
for i:=0 to n do begin
  write(f,Transl[i],' '); u:=L[i];
  while u<>nil do begin
    write(f,Transl[u^.id]:4);
    u:=u^.next
  end;
  writeln(f);
end;}
close(f);
end;

procedure ListProd (P:ListPr; var f :text);
{list opetopic set structure of the product I x P}
var u:List;
    i,s :longint;
begin
  writeln(f,'Dimensions below 0:');
  writeln(f,'-1: the face of dim -1, always 0 (displayed as --)');
  writeln(f,'-2: the type of face: -1 -bottom, 1 - top, 0 - max flag, 2 - p-flag');
  writeln(f,'-3: the dimension of highest non-zero face in the flag');
  s:=1;
  while P<>nil do begin
    for i:=P^.co[-3] downto -3 do
    {if i<>-1 then}
    begin
      u:=P^.next;
      if i=P^.co[-3] then write(f,s:5)
               else write(f,'     ');
      if i=-1 then write(f, '--':4,'| ')
              else write(f, P^.co[i]:4,'| ');
      {if i<>P^.co[-3]  then}
      while u<>nil do begin
        if i<>-1 then write(f, u^.co[i]:4)
                 else write(f, '--':4);
        u:=u^.next;
      end;
      writeln(f);
    end;
    writeln(f);
    P:=P^.nextPr;
    s:=s+1;
  end;
  writeln(f,'Number of faces: ',s-1);
  {readln;}
end;


{SECTION: LIST PROCEDURES for faces in P}

function IsOnTheListPt (u:pt;k:longint):boolean;
var b:boolean;
 begin
   b:=false;
   while (u<>nil) and (not b)  do begin
     b:=(u^.id=k);
     u:=u^.next;
   end;
   IsOnTheListPt:=b;
 end;

 procedure AddToListPt (var u:pt;k:longint);
 var v:pt;
 begin
   new(v); v^.id:=k;
   v^.next:=u; u:=v;
 end;

 procedure Merge(var u:pt; v:pt);
 {adds (without repetitions) elements k on the list v to list u
 and recursively elements from the lists LI[k]; this is used
 by MakeAllIncidencesList to have all incident faces on one list}
 var w:pt;
 begin
   w:=v;
   while w<>nil do begin
     if w^.id<>0 then begin
       if not IsOnTheListPt(u,w^.id) then
         AddToListPt(u,w^.id);
         Merge(u,LI[w^.id])
     end;
     w:=w^.next;
   end;
 end;


{SECTION: GRAPH PROCEDURES}

procedure MakeAllIncidencesList(var LIa,LI:graph);
 {makes lists of all incidences even remote incidences;
 uses LI and makes LIall}
 var i:longint;
 begin
   for i:=0 to max_faces do
     LIa[i]:=nil;
   for i:=1 to n do
     Merge(LIa[i],LI[i]);
 end;

function Count_dimension( k : longint): longint;
  {returns the dimension of the face k in P}
  begin        //write('Nr: ',k);
    if k=0 then Count_dimension := -1
           else Count_dimension := 1+Count_dimension(LI[k]^.id);
  end;

function codom(k:longint; var G:graph):longint;
begin
  codom:=G[k]^.id;
end;

function IsOnPtlist (u:pt; k:longint):boolean;
var b:boolean;
    i:longint;
 begin
   b:=false;
   while (u<>nil) and (not b)  do begin
     b:=b or (u^.id=k);
     u:=u^.next;
   end;
   IsOnPtlist:=b;
 end;


{SECTION: SET_COL and COL OPERATIONS}

procedure zero (var C:set_col);
{sets 0 into set_col array}
  var i,j:longint;
  begin
    for i:=max_dim downto -3 do
      for j:=1 to max_path do
         C[i,j]:=0
  end;

procedure zero2 (var C:set_col2);
{sets 0 into set_col array}
  var i,j:longint;
  begin
    for i:=max_dim downto -3 do
      for j:=1 to 2*max_path do
         C[i,j]:=0
  end;

procedure zeroCol (var C:col);
{sets 0 into set_col array}
  var i:longint;
  begin
    for i:=max_dim downto -3 do
         C[i]:=0
  end;

function inverse(var C,D:set_col;l,di:longint):longint;
{checks if array C is inverse of array D on the part 1 to l,
di - the top dimension of the cell}
var i,j,r : longint;
begin r:=0;
  for i:=1 to l do
    for j:=0 to C[-3,i]{dim} do
      if C[j,i]<>D[j,l-i+1] then r:=j;
  inverse:=r;
end;

function sign(var C:set_col;j,di:longint;var LI:graph ):longint;
{checks the sign of a flag in column j of array C; uses graph LI}
var i,si : longint;
begin si:=1;
 for i:=di downto 1 do begin
   if (LI[C[i,j]]<>nil) then
     if LI[C[i,j]]^.id<>C[i-1,j] then
       begin si:=(-1)*si; {writeln('Good pointer',i:4,j:4,si:4)} end
         {else writeln('Bad pointer! ',i:4,j:4)};
 end;
  sign:=si
end;

procedure AllSigns(var C:set_col;var LI:graph;di:longint );
{calculates all the signs of flags in the table C}
var i : longint;
begin
 for i:=1 to length do begin
   C[di+1,i]:=sign(C,i,di,LI)
 end;
end;

procedure Enumerate(var C:set_col;l:longint);
{enumerates in raw l the comumns in the table C }
var i : longint;
begin
 for i:=1 to length do begin
   C[l,i]:=i
 end;
end;

function diff(var C,D:set_col;i,j,lo,hi:longint;var la:longint):longint;
{Measures the difference between two columns:
-output - number of different places
-la - the highes palace where the difference occurs}
var a,k:longint;
begin a:=0; la:=-1;
  for k:=lo to hi do
    if C[k,i]<>D[k,j] then begin
       a:=a+1; la:=k
    end;
  diff:=a;
end;

procedure test(var C:set_col);
{testing the function diff}
var i,j,a:longint;
    f:text;
begin assign(f,'diff.txt'); rewrite(f);   {writeln('Length: ',length,'!');}
  for i:=1 to (length-1) do
    for j:=i+1 to length do begin
      if  diff(C,C,i,j,0,dim,a)=1 then
      writeln(f,i:4,' ',j:4,diff(C,C,i,j,0,dim,a):4,a:4);
    end;
  close(f);
end;

function distance_one(var C:set_col;dl,dh,l:longint) : longint;
{Checks if the walk is correct, i.e. if the
succesive columns are in the distance one}
var i,a,b:longint;
begin distance_one:=0;
  for i:=1 to l-1 do begin
    b:=diff(C,C,i,i+1,dl,dh,a);
    C[dh+2,i]:=a;
    if (b<>1) then distance_one:=i;
  end;
  C[dh+2,l]:=0;
end;

procedure exchange(var C:set_col;a,b:longint);
{exchanges two columns in array C}
var K:col; i:longint;
begin
  for i:=-1 to dim do K[i]:=C[i,a];
  for i:=-1 to dim do C[i,a]:=C[i,b];
  for i:=-1 to dim do C[i,b]:=K[i];
end;

procedure add_to_list(var C:set_col;Kol:col;l:longint);
{add a column l to array C}
var i:longint;
begin
  for i:=-1 to dim do C[i,l]:=Kol[i];
end;

procedure NumberCol(var C:set_col;d,l:longint);
{numbers l columns in the array C in the raw d}
 var i:longint;
begin
  for i:=1 to l do C[d,i]:=i;
end;

function TopEdges(var C:set_col;dh,l:longint):longint;
{counts top edges in the graph of flags the array C}
 var i,top_ed:longint;
begin
  top_ed:=0; {counts top edges in the graph of flags}
  for i:=1 to l-1 do
    if C[dh+2,i]=dh-1 then top_ed:=top_ed+1;
  TopEdges:=top_ed;
end;

function isEqual (var C,D: col): boolean;
{testin whether two columns are equal}
var b:boolean;
    i:longint;
begin
  b:=C[-3]=D[-3];
  if b then begin
    for i:=-3 to C[-3] do
      b:=b and (C[i]=D[i])
  end;
  isEqual:=b
end;

function isEqual_col (var C,D: set_col;i,j,b,t:longint): boolean;
{testin whether two columns i's and j's are equal from b to t lavel}
var bb:boolean;
    k:longint;
begin
  bb:=true;
    for k:=b to t do
      bb:=bb and (C[k,i]=D[k,j]);
  isEqual_col:=bb;
end;

function meet (var C,D,E: col): boolean;
{calculates intersection of two max flags C and D and
the resulting p-flag returns as E}
var i:longint;
begin
  zeroCol(E);
  if C[-3]<>D[-3] then begin writeln('Bad flag intersection!'); halt end
                  else begin
                         for i:=-3 to C[-3] do
                           if C[i]=D[i] then E[i]:=C[i]
                                        else E[i]:=0;
                         E[-2]:=2;

                       end;
end;

procedure truncCol (var C,D: col; k : longint);
{calculates truncation by k dimensions of a falg C and
the resulting flag returns as D}
var i:longint;
begin
  zeroCol(D);
    for i:=-2 to C[-3]-k do
      D[i]:=C[i];
    D[-3]:=C[-3]-k;
end;

function Check_set_col(var C,D:set_col;di,l:longint):boolean;
var i,j:longint;
    b:boolean;
begin
  b:=true;
  for i:=-3 to di do
    for j:=1 to l do
      b:=b and (C[i,j]=D[i,j]);
  Check_set_col:=b;
end;


{SECTION: LIST OPERATIONS ON LISTS List}

function IsOnTheList (u:List; var C:col):boolean;
var b:boolean;
    i:longint;
 begin
   b:=false;
   while (u<>nil) and (not b)  do begin
     b:=true;
     for i:=-3 to C[-3] do
       b:=b and (u^.co[i]=C[i]);
     u:=u^.next;
   end;
   IsOnTheList:=b;
 end;

procedure AddToList (var u:List ;var C:col);
{add column C at the begining of the list with head u}
var z : List;
 begin
   new(z);
   z^.co:=C;
   z^.next:=u;
   u:=z;
 end;

procedure print_list(w:List);
var i:longint;
begin
  writeln(ff,'State of the list: ');
  while w<>nil do begin
    for i:=-3 to dim do
      write(ff,w^.co[i]:5);
    writeln(ff);
    w:=w^.next;
  end;
    writeln(ff);
end;

function copy_list (u: List):List;
{copy list with head u and the head of the copied list
returns as the value}
var C:longint;
    v,r,s,t:List;
begin
  new(v); r:=v; s:=u;
  while s<>nil do begin
    new(t);
    t^.co:=s^.co;
    r^.next:=t;
    r:=t;
    s:=s^.next;
  end;
  r^.next:=nil;
  copy_list:=v^.next;
  dispose(v);
end;

procedure sym_diff (var u,v,w: List);
{calculates symmetric diffrence of lists List with heads u and v and the
resulting list is returned with the head w;
it assumes some well-behavior of the lists that is special to the present
circumstances}
var i:longint;
    r,s,t:List;
begin
  {first elt from u}
  w:=nil;
  s:=u;
  while  s<>nil do begin
    if not IsOnTheList(v,s^.co) then addToList(w,s^.co);
    s:=s^.next;
  end;
  t:=v;
  while  t<>nil do begin
    if not IsOnTheList(u,t^.co) then addToList(w,t^.co);
    t:=t^.next;
  end;
end;


{SECTION: LOCAL CALCULATIONS OF HAMILTONIAN PATH}

function find_level(var C:set_col; var G : graph; di,co:longint):longint;
 var lev:longint;
begin
  lev:=di-1;
  while (lev>0) and (codom(C[lev+1,co],G)=C[lev,co]) do
    lev:=lev-1;
  find_level:=lev-1;
end;

function find_next_face(var C:set_col; var G : graph; di,level,co:longint):longint;
var u:pt;
    high, low, fa:longint;
begin
  high:=C[level+1,co];
  low:=C[level-1,co];
  u:=G[high];
  while (u<>nil) do begin
    if (IsOnPtlist(G[u^.id],low)) and (C[level,co]<>u^.id)
       then begin fa:=u^.id; u:=nil end
      else u:=u^.next;
  end;
  find_next_face:=fa;
end;

procedure Walk_Local(var C:set_col;var G:graph;k,di,l:longint;var l1:longint);
{Take array C with first flag of a face k in a face structure in LI
that has length of Hamiltonian path l and calculates the rest of
Haminltonian path locally; the length of this new path is returned as l1}
var i,level,fa,m : longint;
begin
  if l> 1 then begin
  l1:=1;
  while (l1=1) or (not isEqual_col(C,C,1,l1,1,di)) do begin
    for i:=0 to di do
      C[i,l1+1]:=C[i,l1];
    l1:=l1+1;
    if l1 mod 2 = 0 then level:=di-1
                   else level:=find_level(C,G,di,l1-1);
    fa:=find_next_face(C,G,di,level,l1);
    C[level,l1]:=fa;
  end;
  end;
end;

{SECTION: CALCULATING ALL FLAGS BETWEEN TWO FACES usig dsf}

procedure DFS_visit(var C:set_col;hi,dh,lo,dl:longint;var K:col;var co:longint);
{used in DFS}
var u:pt;
    i:longint;
begin  K[dh]:=hi;
 {if co mod 50 =0 then  writeln('hi, co, lo',hi:10,co:10,lo:10);}
 if hi=lo then begin add_to_list(C,K,co); co:=co+1 end
 else if dh>dl then begin
   u:=LI[hi];
   while u<>nil do begin
     DFS_visit(C,u^.id,dh-1,lo,dl,K,co);
     u:=u^.next;
   end;
 end;
end;

procedure DFS(var C:set_col; high,low:longint; var len:longint);
{creates in List_col the list of all flags under the face high
over the face low; using DFS_visit1 and add_to_list}
var i,dh,dl:longint;
    Kol: col;
begin
 dh:=face_dim[high]; dl:=face_dim[low];  len:=1;
 for i:=-1 to dh do Kol[i]:=0;
 DFS_visit(C,high,dh,low,dl,Kol,len);
 len:=len-1;
end;


{SECTION: SEARCH FOR HAMILTONIAN PATH + correctness}

procedure walk(var C,D:set_col;l:longint;var t:boolean);
{tries to find a Hamiltonian path C - list of flags; D - Hamiltonian path}
var Free:raw;
    no_file:longint;

function best_sucessor(i:longint):longint;
{finds the highest level where i-th flag D differes 1 from a Free flag in C}
var j,level,lev:longint;
begin level:=-1;
  for j:=1 to l do begin
    if Free[j] and (diff(D,C,i,j,0,dim,lev)=1) then
      if lev>level then level:=lev
  end;
  best_sucessor:=level;
end;

procedure probuj(i:longint; var q : boolean);
{try to find i-th flag in the path; q - end_test}
var k,j,no,la,h:longint;
begin
  {if i mod 3 =0 then writeln(i);}
  k:=0; h:=best_sucessor(i-1);  {write('Bs ',h:2);}
  while (not q) and (k<l) do begin
    k:=k+1;
    if (Free[k]) and (diff(D,C,i-1,k,0,dim,la)=1) and (la=h) then begin
      for j:=-1 to dim do
        D[j,i]:=C[j,k];
        {no_file:=(no_file+1 mod 26);
        write_walk1(D,i,'walk_try'+chr(Ord('a')+no_file)+'.txt');}
      Free[k]:=false;
      if i<l then begin
         {writeln('Probuj: ',i+1);} probuj(i+1,q);
        if not q then begin
          Free[k]:=true;
        end;
      end
      else q:=true;
    end;
  end;
end;

var j:longint;
    b:boolean;
begin {body of the procedure walk}
  for j:=2 to l do Free[j]:=true;
  for j:=-1 to dim do D[j,1]:=C[j,1];
  no_file:=0;
  t:=false;
  Free[1]:=false;
  probuj(2,t);
end;

{SECTION: MAKING FS for I x P}

function Compare_Flags(C,D : col; var Rel : Face_rel) : boolean;
{compares two flags wrt Rel, i.e. their top faces}
 var b:boolean;
 i,max:longint;
begin
  b:=true;
  if C[-3]>D[-3] then max:=C[-3] else max:=D[-3];
  for i:=1 to max do b:=b and (C[i]=D[i]);
  if not b and (C[C[-3]]=D[D[-3]]) then Compare_Flags:=true
  else
  Compare_Flags:=Rel[C[C[-3]],D[D[-3]]];
end;

procedure Zamien_Col(var C,D: col);
var i,k:longint;
begin
  for i:=-3 to max_dim+3 do begin
    k:=C[i];
    C[i]:=D[i];
    D[i]:=k
  end;
end;

procedure Order_faces_codom(P : ListPr; var LI:graph);
{puts codoms first in the lists of faces in I x P}
var u,v,w : List;
    cod,dimm,i,j:longint;
    bb:boolean;
    fff:text;
    Q:ListPr;
begin
  while P<>nil do begin{1}
    if P^.co[-3]>0 then begin{2}
      if P^.co[-2]<>0 then begin{3} {codomian of top, bot of p-flag}
        cod:=LI[P^.co[P^.co[-3]]]^.id;
        u:=P^.next; v:=P^.next;
        while (u<>nil) and (u^.co[u^.co[-3]]<>cod) do
          u:=u^.next;
        if (u<>nil) and (u<>v) then begin Zamien_Col(u^.co,v^.co) end;
      end{3} else begin{4} {codomain of a flag}
        u:=P^.next; v:=P^.next;
        while (u<>nil) and (u^.co[u^.co[-3]-1]<>0) do
          u:=u^.next;
        if (u<>nil) and (u<>v) then
          begin Zamien_Col(u^.co,v^.co) end;
        end;{4}
        end;{2}
    P:=P^.nextPr;
    end;{1}
  end;


procedure Order_faces_dom(P : ListPr; var LI:graph);
{puts doms in a decsreasing orderon the lists of faces in I x P}
var u,v,w : List;
    cod,dimm:longint;
    bb:boolean;
begin
  while P<>nil do begin{1}
        if P^.co[-2]=2 then begin{ex}
          v:=P^.next^.next; dimm:= P^.co[-3]-1; bb:=true;
        while bb do begin{5}
          u:=v;  bb:=false;
          while (u^.next<>nil) do begin{6}
               if  {(u^.co[dimm]=0) or} (u^.co[dimm]<u^.next^.co[dimm]) then
                   begin Zamien_Col(u^.co,u^.next^.co); bb:=true end;
            u:=u^.next;
          end{6};
        end{5};
        end{ex};
    P:=P^.nextPr;
    end;{1}
end;

procedure Difference_p_faces(P : ListPr; var d1,d2:longint);
{puts doms in a decsreasing orderon the lists of faces in I x P}
var u,v,w : List;
    i,dif:longint;
    bb:boolean;
    Q:ListPr;
begin
  while (P^.co[-2]<>2) or (P^.co[P^.co[-3]]<>top) do
    P:=P^.nextPr;
  Q:=P^.nextPr;
  d1:=0; d2:=0;
  while (Q<>nil) and (Q^.co[-2]=2) do begin
    u:=P^.next; v:=Q^.next; dif:=0;
    while (u<>nil) and (v<>nil) do begin
      bb:=true;
      for i:=-2 to u^.co[-3] do
        if u^.co[i]<>v^.co[i] then bb:=false;
      if not bb then dif:=dif+1;
      u:=u^.next;
      v:=v^.next;
    end;
    if dif=1 then d1:=d1+1 else begin d2:=d2+1;
      u:=P^.next; v:=Q^.next;
    end;
    P:=Q;
    Q:=Q^.nextPr;
    end;{1}
end;


procedure Low_Face_Formula(P : ListPr; var d1,d2:longint);
{checking the formula x_n-1 * vec(x)_low = vec(x)_low_(n)
in the lists of faces in I x P}
var u,v,w : List;
    i,fa:longint;
    bb,bc:boolean;
    Q:ListPr;
    fff:text;
begin
  assign(fff,'ZZZ.txt');
  rewrite(fff);
  //writeln('pppooooooooo');
  bb:=true;
  while (P^.co[-2]<>2) or (P^.co[P^.co[-3]]<>top) do
    P:=P^.nextPr;

  d1:=0; d2:=0;  //writeln(P^.co[P^.co[-3]]);
  while (P<>nil) and (P^.co[-2]=2) do begin
    fa:=P^.co[P^.co[-3]-1];
    if fa<>0 then begin{2}
    u:=P^.next;
    //writeln('upsssssss2');
    while (u<>nil) and (u^.co[u^.co[-3]]<>fa) do
      u:=u^.next;
    bc:=true;
      for i:=-2 to u^.co[-3] do
        if u^.co[i]<>P^.co[i] then bc:=false;



    if bc then d1:=d1+1 else begin d2:=d2+1;
       //readln;
      {for i:=u^.co[-3] downto 0 do
        writeln(fff,i:4, u^.co[i]:4, v^.co[i]:4);}
    end;
    //readln;
    //writeln(dif);
    end{2};
    P:=P^.nextPr;
    end;{1}
    close(fff);
end;


procedure Order_faces(P : ListPr; var Rel : Face_rel);
{orders list of faces wrt order in Rel}
var u : List;
    b : boolean;
    q : longint;
    f:text;
begin
  assign(f,Other_Files+'Calculations.txt'); rewrite(f);
  q:=0;
  while P<>nil do begin{1}
    write(f,'P: ');
    write_col(P^.co,f);
    if P^.co[-3]>0 then begin{1.5}
    b:=true;
    while b do begin{2}
      q:=1+q;
      b:=false;
      u:=P^.next;
      if u<>nil then begin{3}
        while u^.next<>nil do begin{4}
          if q<10000 then begin write_col(u^.co,f); write_col(u^.next^.co,f); end;
          writeln(f,' Comparison: ',Compare_Flags(u^.co,u^.next^.co,Rel));
          if not Compare_Flags(u^.next^.co,u^.co,Rel) then begin
             Zamien_Col(u^.co,u^.next^.co);  {nowy parametr}
             b:=true;
          end;
          u:=u^.next;
        end;{4}
      end;{3}
    end;{2}
    end;{1.5}
    P:=P^.nextPr;
    end;{1}
    close(f);
  end;

procedure top_bot (var P,PL: ListPr; var G : graph; side:longint);
{produces faces in the product I x P on sides (-1) - source, (+1) - target}
var u1,u2,u3:ListPr;
    v1,v2:List;
    w:pt;
    i:longint;
begin
  new(u1); u2:=u1; u1^.nextPr:=nil;
  for i:=1 to n do begin
    w:=G[i];  {writeln(i:7, 'Kura!');}
    {u3/i new face represented in a column}
    new(u3);  PL:=u3;
    zeroCol(u3^.co);
    u3^.co[-2]:=side;
    u3^.co[-3]:=Count_dimension(i);
    u3^.co[u3^.co[-3]]:=i;
    u3^.nextPr:=nil;
    u3^.next:=nil;
    u2^.nextPr:=u3;
    u2:=u3;
    if w^.id<>0 then begin
      {adding codomain face of u3/i}
      new(v1);
      zeroCol(v1^.co);
      v1^.co[-2]:=side;
      v1^.co[-3]:=Count_dimension(w^.id);
      v1^.co[v1^.co[-3]]:=w^.id;
      v1^.next:=nil;
      u3^.next:=v1;
      {adding domain faces of u3/i}
      w:=w^.next;
      while w<>nil do begin
        new(v2);
        zeroCol(v2^.co);
        v2^.co[-2]:=side;
        v2^.co[-3]:=Count_dimension(w^.id);
        v2^.co[v2^.co[-3]]:=w^.id;
        v2^.next:=nil;
        v1^.next:=v2;
        v1:=v2;
        w:=w^.next;
      end;
    end;
  end;
  if P=nil then P:=u1^.nextPr
           else begin
             u3:=P;
             while u3^.nextPR<>nil do
               u3:=u3^.nextPr;
             u3^.nextPr:=u1^.nextPr;
           end;
  dispose(u1);
end;

function find_face(var K : col; P:ListPr):List;
var C:col;
    i,s:longint;
    b:boolean;
begin
 {write('find_face: '); write_col(K,17,ff);}
 s:=0;
 find_face:=nil;
 while P<>nil do begin
   s:=s+1;
   b:=true;
   if not isEqual(K,P^.co) then P:=P^.nextPr
               else begin
                      {writeln(ff,'Found! ',s);}
                      find_face:=P^.next;
                      {write_col(P^.co,P^.co[P^.co[-3]],ff);}
                      P:=nil
               end;
 end;
end;

procedure max_flags (var P,PL: ListPr; var C : set_col; k,l:longint);
{for a given face k and its set of maximal flags of length l, the procedure
produces faces and their doms and codoms in the opetopic set with head P
after the last added face pointed by PL; it is assumed here that P<>nil}
var u1,u2,u3:ListPr;
    v1,v2,v3:List;
    i,j,r:longint;
    D1,D2,D3:col;
begin
  for i:=1 to l do begin
    new(u1);       {adding new face (max flag) in I x P}
    zeroCol(u1^.co);
    PL^.nextPr:=u1;
    PL:=u1;
    u1^.NextPr:=nil;
    new(v1); new(v2); new(v3);
    zeroCol(v1^.co); zeroCol(v2^.co);zeroCol(v3^.co);
    for j:=-3 to C[-3,i] do begin
        u1^.co[j]:=C[j,i];
        v1^.co[j]:=C[j,i];
        v2^.co[j]:=C[j,i];
      end;
    u1^.next:=v1; v1^.next:=v2; v2^.next:=v3; v3^.next:=nil;

    if C[-3,i]=0 then begin {dimension 0}
      zeroCol(v1^.co); zeroCol(v2^.co);
      v2^.next:=nil; dispose(v3);
      v1^.co[-2]:=1;
      v2^.co[-2]:=-1;
      v1^.co[0]:=C[0,i];
      v2^.co[0]:=C[0,i];
    end else begin
      {v1 for codom p-flag, v2 for side flag, v3 big side flag}

      v1^.co[v1^.co[-3]-1]:=0; {this is codomain face v1: p-flag}
      v1^.co[-2]:=2;
      v2^.co[v2^.co[-3]]:=0;   {side face flag v2}
      v2^.co[-3]:=v2^.co[-3]-1;
      if (i=1) or (i=l) then begin  {big domain face v3: p-flag}
        zeroCol(v3^.co);
        v3^.co[-3]:=v1^.co[-3];
        v3^.co[v3^.co[-3]]:=k;
        if i=1 then v3^.co[-2]:= -1
               else v3^.co[-2]:= 1;
      end else begin
        if i mod 2 = 0 then r:=1 else r:=-1;
        for j:=-3 to C[-3,i] do begin
          D1[j]:=C[j,i];
          D2[j]:=C[j,i+r];
        end;
        meet(D1,D2,v3^.co);
        end;
      end;
  end;
end;

procedure p_flags (var P,PL: ListPr; var C : set_col; var G:graph; k,l:longint);
{for a given face k and its set of maximal flags of length l, the procedure
produces faces and their doms and codoms}
var u1,u2,Q:ListPr;
    v1,v2,v3,v4:List;
    w:pt;
    i,j,s:longint;
    PC : set_col;
    D1,D2,D3 :col;
begin
  {putting p-flags for k into array PC}
  for i:=1 to l-1 do begin
    zeroCol(D1); zeroCol(D2); zeroCol(D3);
    for j:=-3 to face_dim[k] do begin
      D1[j]:=C[j,i];
      D2[j]:=C[j,i+1];
    end;
    meet(D1,D2,D3);
    for j:=-3 to face_dim[k] do
      PC[j,i]:=D3[j];
  end;
  if face_dim[k]>0 then begin
    {adding 1st face (p-flag) in I x P with top face k}
    new(u1);
    zeroCol(u1^.co);
    for j:=-3 to face_dim[k] do
      u1^.co[j]:=PC[j,1];
    zeroCol(D1); zeroCol(D2);
    D1[-2]:=-1;
    D1[-3]:=face_dim[k];
    D1[face_dim[k]]:=k;
    for j:=-2 to face_dim[k]-1 do
      D2[j]:=C[j,1];
    D2[-3]:=face_dim[k]-1;
    {now: in D1 is -k; in D2 tr_1 of 1st flag for k}
    v1:=copy_list(find_face(D1,P));
    v2:=copy_list(find_face(D2,P));
    sym_diff(v1,v2,v3);
    u1^.next:=v3;
    {add this face with theta to the list of faces of I x P}
    PL^.nextPr:=u1;
    u1^.NextPr:=nil;
    PL:=PL^.nextPr;
    {end of adding 1st flag}
    for i:=2 to l-1 do begin
      v1:=copy_list(find_face(PL^.co,P));
      zeroCol(D2);
      for j:=-3 to C[-3,i] do
        D1[j]:=C[j,i];
      truncCol (D1,D2,1);
      v2:=copy_list(find_face(D2,P));
      sym_diff(v1,v2,v3);

      new(u1);
      zeroCol(u1^.co);
      for j:=-3 to PC[-3,i] do
        u1^.co[j]:=PC[j,i];
      u1^.next:=v3;
      PL^.nextPr:=u1;
      PL:=u1;
    end;
  end;
end;

procedure check_tests (var P: ListPr; var f:text);
{this procedure check whether the p-flags C that are faces of p-flags D
have below the zero in C the same faces as in the p-flag D}
var u:ListPr;
    v:List;
    w:pt;
    i,j,s:longint;
    D1,D2,D3 :col;
    below_zero:boolean;
begin
  u:=P;
  below_zero:=true;
  while u<>nil do begin
    v:=u^.next;
    D1:=u^.co;
    while v<>nil do begin
      D2:=v^.co;
      if D2[-2]=2 then begin
        i:=0;
        while D2[i]<>0 do i:=i+1;
        for i:=0 to i-1 do
          if D1[i]<>D2[i] then below_zero:=false;
      end;
      v:=v^.next;
    end;
      u:=u^.nextPr;
  end;
  if below_zero then write(f,'Below 0 is OK')
                else begin write(f,'Below 0 is NOT OK'); write('NO '); readln end;
end;


procedure p_flags_codoms (var P,PL: ListPr; var C : set_col; var G:graph; k,l:longint);
{NOT USED NOW}
{for a given face k and its set of maximal flags of length l,
the procedure produces faces and their codoms ONLY;
the procdure p_flags calculates both codoms and dom}
var u1,u2:ListPr;
    v1,v2,v3,v4:List;
    w:pt;
    i,j,s:longint;
    PC : set_col;
    D1,D2,D3 :col;
begin
  for i:=1 to l-1 do begin
    for j:=-3 to face_dim[k] do begin
      D1[j]:=C[j,i];
      D2[j]:=C[j,i+1];
    end;
    meet(D1,D2,D3);
    for j:=-3 to face_dim[k] do
      PC[j,i]:=D3[j];
  end;

  {Adding just codomains}
  for i:=1 to l-1 do begin{*}
    new(u1);       {adding new face (p-flag) in I x P}
    PL^.nextPr:=u1;
    PL:=u1;
    u1^.NextPr:=nil;
    new(v1);
    u1^.next:=v1;
    v1^.next:=nil;
    for j:=-3 to face_dim[k] do
      u1^.co[j]:=PC[j,i];
    v1^.co:=u1^.co;
    if v1^.co[v1^.co[-3]-1]=0 then begin
      {p-flag with codim 1 hole; formula from the notes}
      v1^.co[v1^.co[-3]-2]:=0;
      v1^.co[v1^.co[-3]-1]:= LI[v1^.co[v1^.co[-3]]]^.id;
      v1^.co[v1^.co[-3]]:=0;
    end else
    begin
      {p-flag with codim more than 1 hole;  formula from the notes}
      v1^.co[v1^.co[-3]-1]:= LI[v1^.co[v1^.co[-3]]]^.id;
      v1^.co[v1^.co[-3]]:=0;
    end;
  end;{*}
end;


{SECTION: CALCULATION OF ORDERS}

procedure Check_Rel(var f:text; var Fa : Face_rel;s:string);
var i,j,k:longint;
    b:boolean;
begin
  writeln(f,s);
  b:=true;
  for i:=1 to n do
      b:=b and Fa[i,i];
  if b then writeln(f,'Reflexive: yes!') else writeln(f,'Reflexive: no!');

  b:=true;
  for i:=1 to n do
    for j:=1 to n do
      for k:=1 to n do
        b:=b and ((Fa[i,j] and Fa[j,k])<= Fa[i,k]);
  if b then writeln(f,'Transitive: yes!') else writeln(f,'Transitive: no!');

  b:=true;
  for i:=1 to n do
    for j:=1 to n do
      b:=b and (Fa[i,j] or Fa[j,i]);
  if b then writeln(f,'Connected: yes!') else writeln(f,'Connected: no!');

  b:=true;
  for i:=1 to n do
    for j:=1 to n do
      b:=b and ((Fa[i,j] and Fa[j,i])<=Fa[i,i]);
  if b then writeln(f,'Weakly antysymmetric: yes!')
       else writeln(f,'Antysymmetric: no!');
end;


procedure Write_Rel (var f : text; var Fa : Face_rel; s : string);
var i,j:longint;
begin
writeln(f,s);
   write(f,'   ');
   for i:= 1 to n do
    write(f,i:3);
  writeln(f);
  for i:= 1 to n do begin
    write(f,i:3);
    for j:=1 to n do
      if Fa[i,j] then write(f,'  1') else write(f,'  0');
    writeln(f);
  end;
end;

procedure Write_Order (var f:text; var Fa : Face_Order; s : string);
var i:longint;
begin
 writeln(f,s);
 for i:= 1 to n do
 write(f,Fa[i]:3);
 writeln(f);
end;

procedure Buble_Face_rel(var Fa : Face_Order; var Rel: Face_rel);
{odering faces according to the relation Rel}
var i,j,a:longint;
begin
  for i:=1 to n-1 do
    for j:=1 to n-i do begin
      if Rel[Fa[j+1],Fa[j]] then begin
         a:=Fa[j];
         Fa[j]:=Fa[j+1];
         Fa[j+1]:=a;
      end;
    end;
end;

procedure Quick_Face_rel(var Fa : Face_Order; var Rel: Face_rel);
function Quick_Partition(var Fa: Face_Order;var Rel:Face_rel; l,r:longint):longint;
var i,j,pi,a:longint;
begin
  pi:=Fa[l];
  i:=l; j:=r;
  while i<j do begin
    while Rel[pi,Fa[j]] do j:=j-1;
    while Rel[Fa[i],pi] do i:=i+1;
    if i<j then begin
      a:=Fa[i];
      Fa[i]:=Fa[j];
      Fa[j]:=a;
    end;
  end;
  Quick_Partition:=j;
end;
procedure Quick(var Fa: Face_Order;var Rel: Face_rel; l,r:longint);
var a,mi:longint;
begin
  if l<r then begin
    mi:=Quick_Partition(Fa,Rel,l,r);
    Quick(Fa,Rel,l,mi);
    Quick(Fa,Rel,mi+1,r);
  end;
end;
begin
  Quick(Fa,Rel,1,n);
end;

procedure UpLowGlob_generators (var OpeArr : OpetopeTab; var Up, Low, Glob : Face_rel);
{puts generators for upper and lower order into arrays Up and Low;}
var i,j:longint;
    u,v:DomList;
begin
  for i:=1 to n do
    for j:=1 to n do begin
      Up[i,j]:=false;
      Low[i,j]:=false;
      Glob[i,j]:=false;
    end;
  for i:=1 to n do begin
      u:=OpeArr[i]^.dom;
      Glob[i,OpeArr[i]^.cod^.face]:=true; {face is smaller than its codomain}
      while u<>nil do begin
        Up[u^.FaceDom^.face,OpeArr[i]^.cod^.face]:=true;
        Glob[u^.FaceDom^.face,OpeArr[i]^.cod^.face]:=true;
        Glob[u^.FaceDom^.face,i]:=true; {face is larger than its domains}
        u:=u^.nextDom;
      end;
      u:=OpeArr[i]^.codOf;
      while u<>nil do begin
        v:=OpeArr[i]^.domOf;
        while v<>nil do begin
          Low[u^.FaceDom^.face,v^.FaceDom^.face]:=true;
          Glob[u^.FaceDom^.face,v^.FaceDom^.face]:=true;
          v:=v^.nextDom;
        end;
        u:=u^.nextDom;
      end;
  end;
end;

procedure Refl_Closure (var C : Face_rel);
var i,j,k:longint;
begin
  for i:=1 to n do
    C[i,i]:=true;
end;

procedure Trans_Closure (var C : Face_rel);
var i,j,k:longint;
    b:boolean;
begin
  b:=false;
  while not b do begin
    b:=true;
    for i:=1 to n do
      for j:=1 to n do
        for k:=1 to n do begin
          if C[i,j] and C[j,k] then begin
            b:=b and C[i,k];
            C[i,k]:=true;
          end;
        end;
  end;
end;


{SECTION: INPUT PROCEDURES}

procedure read_trans(var Tr : Names);
{reads translation of numbers to other names}
var i,a:longint;
    s:string[3];
    c:char;
    f:text;
begin
  assign(f,translation);
  reset(f);
  for i:=0 to n do begin
    s:=''; c:='a';
    while c<>' ' do begin
      read(f,c);
      if c<>' ' then s:=s+c;
    end;
    readln(f,a);
    Tr[a]:=s;
  end;
  close(f);
end;

procedure get_face_structure(var LIz:graph; ope:string; bb:boolean);
{constants for the opetopes and reads face structure}
var v,u:pt;
    f:text;
    a,b,c:longint;
    d:char;
    p:boolean;
    t,input_graph:string;
    x,y:DomList;
    z:OpetopeList;
begin
   {Initialization of the constants}
   assign(f,ope); {file with the opetopes parameters}
   reset(f);
   readln(f,dim);
   readln(f,n);
   readln(f,top);
   if bb then begin
     writeln('Dimension: ',dim);
     writeln('Number of faces: ',n);
     writeln('Number of top face: ',top);
   end;
     input_graph:=''; translation:=''; walk_file:='';
   read(f,d);
   while  d<>' ' do begin
     input_graph:=input_graph+d;
     read(f,d);
   end;
   readln(f);
   read(f,d);
   while  d<>' ' do begin
     translation:=translation+d;
     read(f,d);
   end;
   readln(f);
   read(f,d);
   p:=true;
   while  d<>' ' do begin
     walk_file:=walk_file+d;
     if d='.' then p:=false;
     if p then Other_files:=Other_files+d;
     read(f,d);
   end;
   close(f);
  {Reading graph as an array of lists and as a lined structure}
  TopFace:=nil;
  for a:=0 to n do begin
    new(OpetopeArray[a]);
    OpetopeArray[a]^.face:=a;
    OpetopeArray[a]^.cod:=nil;
    OpetopeArray[a]^.dom:=nil;
    OpetopeArray[a]^.codOf:=nil;
    OpetopeArray[a]^.domOf:=nil;
  end;
  //writeln('Cos: ',input_graph);
  assign(f,input_graph);
  reset(f);
  {begining of the new vesion}
  while not eof(f) do begin
    read(f,a,b); {read face and its codomain}
    new(LIz[a]);  LIz[a]^.id:=b; LIz[a]^.next:=nil; v:=LIz[a];
    OpetopeArray[a]^.cod:=OpetopeArray[b];
    new(x);
    x^.FaceDom:=OpetopeArray[a];
    x^.nextDom:=OpetopeArray[b]^.codOf;
    OpetopeArray[b]^.codOf:=x;

    {read faces in the domain of a}
    while not seekeoln(f) do begin
      new(u); read(f,u^.id); u^.next:=nil; v^.next:=u; v:=u;
      {OpetopeArray[a]^.dom:=u^.id;}
      new(x);
      x^.FaceDom:=OpetopeArray[u^.id];
      x^.nextDom:=OpetopeArray[a]^.dom;
      OpetopeArray[a]^.dom:=x;
      new(x);
      x^.FaceDom:=OpetopeArray[a];
      x^.nextDom:=OpetopeArray[u^.id]^.domOf;
      OpetopeArray[u^.id]^.domOf:=x;
    end;
    readln(f);
  end;
  {end of the new vesion}
  {Old version}
  {while not eof(f) do begin
    read(f,a);
    LIz[a]:=nil;  v:=nil;
    while not seekeoln(f) do begin
      new(u); read(f,u^.id); u^.next:=nil;
      if LIz[a]=nil then LIz[a]:=u
                   else v^.next:=u;
      v:=u;
    end;
    readln(f);
  end;}
  close(f);
end;


{SECTION: INICIALIZATION}

procedure ini(ope:string; b:boolean);
{inicialization of variables; reading data;
produces test file of what has been read}
var i,j:longint;
    f:text;
begin
  Other_Files:='';
  All_correct:=true;
  get_face_structure(LI,ope,b);

  {read_trans(Transl);}
  list_face_structure(LI,'Faces.txt');
  MakeAllIncidencesList(LIall,LI);
  list_face_structure(LIall,'FacesAll.txt');
  for i:=0 to n do  begin
    face_dim[i]:=Count_dimension(i);
  end;
  Product:=nil;
  ProductLast:=nil;

  {Calculation of Orders}
  assign(f,Other_Files+'Orders.txt'); rewrite(f);
  UpLowGlob_generators (OpetopeArray,UpperRel, LowerRel, GlobalRel);
  {write_rel(f,LowerRel,'Lower generators: ');
  write_rel(f,UpperRel,'Upper generators: ');
  write_rel(f,GlobalRel,'Global generators: ');}
  for i:=1 to n do begin
    Upper[i]:=i;
    Lower[i]:=i;
    Global[i]:=i;
  end;
  {Reflexive and Transitive Closures}
  Trans_closure(GlobalRel);
  Refl_closure(GlobalRel);
  {Trans_closure(LowerRel);
  Refl_closure(LowerRel);
  Trans_closure(UpperRel);
  Refl_closure(UpperRel);}

  write_rel(f,GlobalRel,'Global: ');
  Buble_Face_rel(Global,GlobalRel);
  {Buble_Face_rel(Lower,LowerRel);
  Buble_Face_rel(Upper,UpperRel);}

  {Write_Order(f,Lower,'Lower: ');
  Write_Order(f,Upper,'Upper: ');}
  Write_Order(f,Global,'Global: ');
  Check_Rel(f,GlobalRel,'Global: ');

  for i:=0 to face_dim[Top] do begin
    for j:=1 to n do
      if face_dim[Global[j]]=i then write(f,Global[j]:4);
    writeln(f);
  end;

  close(f);
end;


{SECTION: MENU}

procedure menu1;
var a,te : longint;
    b : boolean;
begin
writeln('   Menu1: ');
  assign(ff,Other_Files+'HamPath.txt'); rewrite(ff);
  zero(List_col);
  DFS(List_col,top,0,length);

  //writeln(ff,'Maximal flags as they come from DFS: ');
  //write_set_col(List_col,face_dim[top]+3,0,1,length,ff);  {Listing flags just from DFS}
  //writeln(ff, 'End of max flags unordered!');   writeln(ff);

  Walk(List_col,Walk_col,length,b); {finds top path}
  {Finds inverse path:  calculates walk starting from
  `delta of gamma's of the top', i.e. from the last of List_col}
  //List_col1:=Walk_col;
  //exchange(List_col1,1,length);
  //Walk(List_col1,Walk_col1,length,b);
  {writeln(ff,'A list inversed:');
  write_set_col(Walk_col1,face_dim[top]+3,0,1,length,ff);}

  AllSigns(Walk_col,LI,face_dim[top]); {fills dim+1 level}
  a:=distance_one(Walk_col,0,face_dim[top],length); {fills dim+2 level; counts distance of columns}
  NumberCol(Walk_col,face_dim[top]+3,length); {fills dim+3 level}

  write_set_col(Walk_col,face_dim[top]+3,0,1,length,ff);

  if a=0 then writeln(ff,'Correct walk!')
    else begin writeln(ff,'Incorrect walk! Walk breaks at column ',a);
      writeln('Incorrect walk!',top);
    end;
  te:=TopEdges(Walk_col,face_dim[top],length);
  {writeln(ff,'Top edges and ratio: ',te:5,'  ', length / te:4:2);}
  writeln(ff,'Inverse: ',inverse(Walk_col,Walk_col1,length,face_dim[top]));
  close(ff);
end;

procedure menu2;
var a,te,i,j : longint;
    b : boolean;
    C,D,E:Col;
    X:Set_Col2;
begin
writeln('   Menu2: ');
  assign(ff,Other_Files+'HamPathPlus.txt'); rewrite(ff);
  zero(List_col);
  DFS(List_col,top,0,length);

  Walk(List_col,Walk_col,length,b);
  for i:=1 to length do
    for j:=0 to face_dim[top] do
      Walk_col2[j,2*i-1]:=Walk_col[j,i];
  for i:=1 to length-1 do begin
    for j:=0 to face_dim[top] do begin
      C[j]:=Walk_col[j,i];
      D[j]:=Walk_col[j,i+1];
    end;
    C[-3]:=face_dim[top]; D[-3]:=face_dim[top];
    meet(C,D,E);
    for j:=0 to face_dim[top] do
      Walk_col2[j,2*i]:=E[j];
  end;
   for i:=1 to 2*length-1 do begin
    Walk_col2[face_dim[top]+1,i]:=i;
    end;
  write_set_col2(Walk_col2,face_dim[top]+1,0,1,2*length-1,ff);
  close(ff);

  {making p-flags only file}
  assign(ff,Other_Files+'_p_flags.txt'); rewrite(ff);
  for i:=1 to length-1 do
    for j:=-3 to face_dim[top]+3 do
    X[j,i]:=Walk_col2[j,2*i];
  write_set_col2(X,face_dim[top]+1,0,1,length-1,ff);
  {write_set_col3(Walk_col2,face_dim[top]+1,0,1,2*length-1,ff);}
  close(ff);
end;

procedure menu3;
var a,te,fa:longint;
    b:boolean;
begin
  writeln('   Menu3: ');
  assign(ff,Other_Files+'AllPaths.txt'); rewrite(ff);
  for fa:=top downto 1 do begin
    zero(List_col);
    DFS(List_col,fa,0,length);
    {write_set_col(List_col,face_dim[top],0,1,length,ff);}

    Walk(List_col,Walk_col,length,b);
      exchange(List_col1,1,length);
  Walk(List_col1,Walk_col1,length,b);

    AllSigns(Walk_col,LI,face_dim[fa]); {fills dim+1 level}
    a:=distance_one(Walk_col,0,face_dim[fa],length); {fills dim+2 level; counts distance of columns}
    NumberCol(Walk_col,face_dim[fa]+3,length); {fills dim+3 level}

    write_set_col(Walk_col,face_dim[fa]+3,0,1,length,ff);

    if a=0 then writeln(ff,'Correct walk!')
      else writeln(ff,'Incorrect walk! Walk breaks at column ',a);
    if face_dim[fa]>0 then begin
      te:=TopEdges(Walk_col,face_dim[fa],length);
      writeln(ff,'Inverse: ',inverse(Walk_col,Walk_col1,length,face_dim[fa]));
      writeln(ff,'Top edges and ratio: ',te:5,'  ', te/length:4:2);
    end;
  writeln(ff);
  end;
  writeln(ff,'Top raw - flag number');
  writeln(ff,'Top-1 raw - level of change between flags');
  writeln(ff,'Top-2 raw - sign of the flag');
  writeln(ff,'Remaining raws - the flag');
  close(ff);
end;

procedure menu4;
var i,fa,di,d1,d2:longint;
    b:boolean;
    P:ListPr;
begin
  writeln('   Menu4: ');
  assign(ff,Other_Files+'ProdFaces.txt'); rewrite(ff);
  {Make the list of lists of thetas of faces in I x P???}
  {All for top and bottom}
  top_bot(Product,ProductLast,LI,-1);
  top_bot(Product,ProductLast,LI,1);

  {List all flags of all their faces (of codim 1)}

  for fa:=1 to top do begin
    zero(List_col);
    DFS(List_col,fa,0,lengths[fa]);
    new(Order[fa]);
    zero(Order[fa]^);
    di:=count_dimension(fa);
    Walk(List_col,Order[fa]^,lengths[fa],b);
    for i:=1 to lengths[fa] do {dimension of the flags}
      Order[fa]^[-3,i]:=di;
    max_flags(Product,ProductLast,Order[fa]^,fa,lengths[fa]);
  end;
  {List all flags of all their faces (of codim 1)}
  for fa:=1{top} to top do  begin
    if lengths[fa]>1 then
    p_flags(Product,ProductLast,Order[fa]^,LI,fa,lengths[fa]);
  end;
  {Order list faces of codim 1}
  {ListProd (Product,ff);}
  Order_faces_codom(Product,LI);

  {write it to ff file}
  {ListProd (Product,ff);}

  Order_faces_dom(Product,LI);
  ListProd (Product,ff);

  Difference_p_faces(Product,d1,d2);
  writeln(ff,'Difference 1: ',d1:5,'   (number of different p-flags in theta`s of consequtive p-flags is 1)');
  writeln(ff,'Difference 2: ',d2:5,'   (number of different p-flags in theta`s of consequtive p-flags is NOT 1)');

  {checking a formula  }
  Low_Face_Formula(Product,d1,d2);
  writeln(ff,'Good cases: ',d1:5,'  (  x_n-1 * (vec(x)_low) = (vec(x)_low)_(n) )');
  writeln(ff,'Bad cases: ',d2:5);
  if d2<>0 then begin writeln('Bad!'); readln;  end;
  Check_tests(Product,ff);
  close(ff);
end;

procedure menu5;
var a,te,length1 : longint;
    b : boolean;
    hh:text;
begin
writeln('   Menu5: ');
  assign(hh,Other_Files+'HamPathCheck.txt'); rewrite(hh);
  zero(List_col);
  DFS(List_col,top,0,length);
  Walk(List_col,Walk_col,length,b); {finds top path}
  for a:=-3 to face_dim[top] do
    Walk_col1[a,1]:=List_col[a,1];
  Walk_Local(Walk_col1,LI,top,face_dim[top],length,length1);
  {**Constract top Hamiltonian path locally}

  AllSigns(Walk_col,LI,face_dim[top]); {fills dim+1 level}
  a:=distance_one(Walk_col,0,face_dim[top],length); {fills dim+2 level; counts distance of columns}
  NumberCol(Walk_col,face_dim[top]+3,length); {fills dim+3 level}

  write_set_col(Walk_col,face_dim[top]+3,0,1,length,hh);
  if a=0 then writeln(hh,'Correct walk!')
    else writeln(hh,'Incorrect walk! Walk breaks at column ',a);
  te:=TopEdges(Walk_col,face_dim[top],length);
  writeln(hh,'Local walk: ');
  AllSigns(Walk_col1,LI,face_dim[top]); {fills dim+1 level}
  a:=distance_one(Walk_col1,0,face_dim[top],length); {fills dim+2 level; counts distance of columns}
  NumberCol(Walk_col1,face_dim[top]+3,length); {fills dim+3 level}
  write_set_col(Walk_col1,face_dim[top]+3,0,1,length,hh);

  {**Check whether both ways of calculating top Hamiltonian path are equal}
  if  Check_set_col(Walk_Col,Walk_Col1,face_dim[top],length) then
        writeln(hh,'Local is Global!')
     else
        begin writeln(hh,'Local is NOT Global!');
          writeln('Local is NOT Global!'); {readln;}
        end;
  close(hh);
end;

procedure menu11;
var a,te,length1 : longint;
    b : boolean;
    hh:text;
begin
  writeln('   Menu11: ');
  menu1; menu2; menu3; menu4; menu5;
end;

procedure menu12;
var a,te,length1 : longint;
    b : boolean;
    hh:text;
    s:string;
    c:char;
begin
  assign(hh,'AListOfOpetopes.txt');
  reset(hh);
  writeln('   Menu12: ');
  while not eof(hh) do begin
    readln(hh,s);
    writeln('Opetope '+s);
    Other_files:='Data'+s;
    s:='Data'+s+'Opetope.txt';
    writeln(s);
    ini(s,false);
    {list_face_structure(LI);}
    menu1;
    menu2;
    menu3;
    menu4;
    menu5;
    {readln;}
  end;
  close(hh);
end;

procedure menu21;
var fa : longint;
    x : DomList;
begin
writeln('   Menu21: ');
  fa:=1;
  while fa>0 do begin
    write('Number of face to test: '); readln(fa);
    writeln('Face: ',fa:4);
    writeln('Codomain: ',OpetopeArray[fa]^.cod^.face:4);
    write('Domain: ');
    x:=OpetopeArray[fa]^.dom;
    while x<>nil do begin
      write(x^.FaceDom^.face : 4);
      x:=x^.nextDom;
    end;
    writeln;
    write('Codomain of: ');
    x:=OpetopeArray[fa]^.codOf;
    while x<>nil do begin
      write(x^.FaceDom^.face : 4);
      x:=x^.nextDom;
    end;
    writeln;
    write('Domain of: ');
    x:=OpetopeArray[fa]^.domOf;
    while x<>nil do begin
      write(x^.FaceDom^.face : 4);
      x:=x^.nextDom;
    end;
    writeln;
  end;
end;

procedure display_menu;
begin
  writeln('   Menu: ');
  writeln('0  - End');
  writeln('1  - Top Hamiltonian Path of the top face');
  writeln('2  - Top Hamiltonian Path with p-falgs of the top face');
  writeln('3  - Top Hamiltonian Path of all faces');
  writeln('4  - Face structure of the product I x P');
  writeln('5  - Top Hamiltonian Path of the top face both ways (global and local)');
  writeln('11 - All the above');
  writeln('12 - All the above for all the opetpes listed');
  writeln('21 - Check fs');
end;

procedure menu;
 var a :longint;
 begin
  {ClrScr;}
  a:=10;
  {display_menu;}
  while a<>0 do begin
  display_menu;
  write('Chose from menu: ');
  readln(a);
  case a of
    1: menu1;
    2: menu2;
    3: menu3;
    4: menu4;
    5: menu5;
    11: begin menu11; a:=0 end;
    12: begin menu12; a:=0 end;
    21: menu21;
  end;
  end;
end;


{SECTION: main program}
var f:text;
    b:boolean;
    i:longint;
    ans:char;
begin
  Clrscr;
  ini(opetope_file,true);
  menu;
end.

To Do Now:
     1. Write a separate procedure for a parametrized search for Ham Path
        between two faces
Menu:
3. All pairs top Hamiltonian Path of flags
4. All pairs of difference of dimension k of top Hamiltonian Path of flags

6. Check whether two faces in possibly different face structures
   generate isomorphic sub-opetopes


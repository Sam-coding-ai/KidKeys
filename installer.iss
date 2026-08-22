[Setup]
AppName=KidKeys Toddler Locker
AppVersion=1.0
AppPublisher=KidKeys
DefaultDirName={autopf}\KidKeys
DefaultGroupName=KidKeys
OutputBaseFilename=KidKeys_Setup
Compression=lzma
SolidCompression=yes
OutputDir=.

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\KidKeys.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\KidKeys"; Filename: "{app}\KidKeys.exe"
Name: "{autostartup}\KidKeys"; Filename: "{app}\KidKeys.exe"
Name: "{autodesktop}\KidKeys"; Filename: "{app}\KidKeys.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\KidKeys.exe"; Description: "Launch KidKeys Toddler Locker"; Flags: nowait postinstall skipifsilent

[Code]
var
  DonateButton: TNewButton;
  SubscribeButton: TNewButton;
  PromoLabel: TNewStaticText;

procedure DonateOnClick(Sender: TObject);
var
  DonatePopup: TForm;
  DetailsBox: TNewMemo;
  CloseBtn: TNewButton;
  HeaderLabel: TNewStaticText;
begin
  DonatePopup := TForm.Create(WizardForm);
  try
    DonatePopup.Caption := 'Support KidKeys 💖';
    DonatePopup.ClientWidth := ScaleX(440);
    DonatePopup.ClientHeight := ScaleY(280);
    DonatePopup.Position := poMainFormCenter;
    DonatePopup.BorderStyle := bsDialog;
    
    HeaderLabel := TNewStaticText.Create(DonatePopup);
    HeaderLabel.Parent := DonatePopup;
    HeaderLabel.Top := ScaleY(15);
    HeaderLabel.Left := ScaleX(20);
    HeaderLabel.Width := ScaleX(400);
    HeaderLabel.WordWrap := True;
    HeaderLabel.Font.Style := [fsBold];
    HeaderLabel.Font.Color := clNavy;
    HeaderLabel.Caption := 'KidKeys is 100% free, but keeping tiny hands at bay takes late-night coding! 🍼💻 If this app saved your sanity, consider supporting the developer:';
    
    DetailsBox := TNewMemo.Create(DonatePopup);
    DetailsBox.Parent := DonatePopup;
    DetailsBox.SetBounds(ScaleX(20), ScaleY(65), ScaleX(400), ScaleY(160));
    DetailsBox.ReadOnly := True;
    DetailsBox.WordWrap := True;
    DetailsBox.ScrollBars := ssVertical;
    DetailsBox.Font.Name := 'Consolas'; 
    
    DetailsBox.Text := 'Bitcoin Address:' + #13#10 + 
                       '16DYQP8LwdVGzcmNoWq6haUcsVUuUXMKY1' + #13#10 + #13#10 + 
                       'EVM Address (USDT, USDC, ETH, BNB):' + #13#10 + 
                       '0x0163613124b4e5027e4c2122e9e0cbd7fc773458';
                       
    CloseBtn := TNewButton.Create(DonatePopup);
    CloseBtn.Parent := DonatePopup;
    CloseBtn.Width := ScaleX(120);
    CloseBtn.Height := ScaleY(30);
    CloseBtn.Left := (DonatePopup.ClientWidth - CloseBtn.Width) div 2;
    CloseBtn.Top := ScaleY(235);
    CloseBtn.Caption := 'Awesome, Thanks!';
    CloseBtn.Font.Style := [fsBold];
    CloseBtn.ModalResult := mrOk;
    
    DonatePopup.ShowModal;
  finally
    DonatePopup.Free;
  end;
end;

procedure SubscribeOnClick(Sender: TObject);
var
  SubPopup: TForm;
  DetailsBox: TNewMemo;
  CloseBtn: TNewButton;
  HeaderLabel: TNewStaticText;
begin
  SubPopup := TForm.Create(WizardForm);
  try
    SubPopup.Caption := 'Join the Magic ✨';
    SubPopup.ClientWidth := ScaleX(380);
    SubPopup.ClientHeight := ScaleY(215);
    SubPopup.Position := poMainFormCenter;
    SubPopup.BorderStyle := bsDialog;
    
    HeaderLabel := TNewStaticText.Create(SubPopup);
    HeaderLabel.Parent := SubPopup;
    HeaderLabel.Top := ScaleY(15);
    HeaderLabel.Left := ScaleX(20);
    HeaderLabel.Width := ScaleX(340);
    HeaderLabel.WordWrap := True;
    HeaderLabel.Font.Style := [fsBold];
    HeaderLabel.Font.Color := clGreen;
    HeaderLabel.Caption := 'Don''t miss out on the magic! Join our Telegram family for the latest updates and to request new features. 🚀';
    
    DetailsBox := TNewMemo.Create(SubPopup);
    DetailsBox.Parent := SubPopup;
    DetailsBox.SetBounds(ScaleX(20), ScaleY(75), ScaleX(340), ScaleY(85));
    DetailsBox.ReadOnly := True;
    DetailsBox.WordWrap := True;
    
    DetailsBox.Text := 'Copy this link to join our official community:' + #13#10 + #13#10 + 
                       'https://t.me/kidkeysofficial or search in telegram @kidkeysofficial ';
                       
    CloseBtn := TNewButton.Create(SubPopup);
    CloseBtn.Parent := SubPopup;
    CloseBtn.Width := ScaleX(100);
    CloseBtn.Height := ScaleY(30);
    CloseBtn.Left := (SubPopup.ClientWidth - CloseBtn.Width) div 2;
    CloseBtn.Top := ScaleY(170);
    CloseBtn.Caption := 'I''m In!';
    CloseBtn.Font.Style := [fsBold];
    CloseBtn.ModalResult := mrOk;
    
    SubPopup.ShowModal;
  finally
    SubPopup.Free;
  end;
end;

procedure InitializeWizard;
begin
  PromoLabel := TNewStaticText.Create(WizardForm);
  PromoLabel.Parent := WizardForm;
  PromoLabel.Left := ScaleX(15);
  PromoLabel.Top := WizardForm.CancelButton.Top - ScaleY(25);
  PromoLabel.Caption := '✨ Did KidKeys save your sanity? Support the developer and join the community!';
  PromoLabel.Font.Color := clNavy; 
  PromoLabel.Font.Style := [fsBold];

  DonateButton := TNewButton.Create(WizardForm);
  DonateButton.Parent := WizardForm;
  DonateButton.Left := ScaleX(15);
  DonateButton.Top := WizardForm.CancelButton.Top;
  DonateButton.Width := ScaleX(150);
  DonateButton.Height := WizardForm.CancelButton.Height;
  DonateButton.Caption := '💖 Support Developer';
  DonateButton.Font.Style := [fsBold];
  DonateButton.OnClick := @DonateOnClick;

  SubscribeButton := TNewButton.Create(WizardForm);
  SubscribeButton.Parent := WizardForm;
  SubscribeButton.Left := DonateButton.Left + DonateButton.Width + ScaleX(10);
  SubscribeButton.Top := WizardForm.CancelButton.Top;
  SubscribeButton.Width := ScaleX(140);
  SubscribeButton.Height := WizardForm.CancelButton.Height;
  SubscribeButton.Caption := '⭐ Get Updates';
  SubscribeButton.Font.Style := [fsBold];
  SubscribeButton.OnClick := @SubscribeOnClick;
end;
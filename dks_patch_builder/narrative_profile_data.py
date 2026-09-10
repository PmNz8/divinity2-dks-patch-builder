# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Frozen recognized GOG Developer's Cut corpus and fixed FoV debt inputs.

Metadata only; no game assets. Based on accepted source reports 2026-09-10.
Both tools vendor this exact profile; unknown sources/overlays fail closed.
"""

PROFILE = {
  "profile_id": "gog-dc-fov-debt-v1",
  "deployment": "new-game-fov",
  "archive_count": 533,
  "archives": [
    {
      "path": "Characters.dv2",
      "size": 146767872,
      "sha256": "2f0c3a614d2fc1bf553faa4fcf4a9303c44404a2963723cbbde7637730a1ced8",
      "entries": 746
    },
    {
      "path": "CharacterTemplates.dv2",
      "size": 302350336,
      "sha256": "96b7670ecb96a50910b5ce6cc766f92aac0559091c14b9b7780246c450acc3b5",
      "entries": 324
    },
    {
      "path": "CompiledAssets.dv2",
      "size": 197230592,
      "sha256": "3267a92109b111fa9b4194e4e8e32ebd945157c26c774d124c7c09659ad1b9bb",
      "entries": 473
    },
    {
      "path": "Effects.dv2",
      "size": 22642688,
      "sha256": "97cea731793cfece9daf71b7407564e3ad1bb4c7ac148cd1cc9e7c90b959dc9e",
      "entries": 378
    },
    {
      "path": "Episode_1_Extended/DialogData.dv2",
      "size": 2392064,
      "sha256": "1264e7da2516c4eaeb398053456d2cb8bb7a2b518176a023968c597bb0017daf",
      "entries": 824
    },
    {
      "path": "Episode_1_Extended/Dialogs.dv2",
      "size": 597753856,
      "sha256": "02de3e8686c271c7d74487c47b6fb53197f7c37f0fedff47c9ce6095ae956b28",
      "entries": 2097
    },
    {
      "path": "Episode_1_Extended/InitSaveGame.dv2",
      "size": 1114112,
      "sha256": "380d85d83203690e314fedf6cb5b0c6cc6933545aeec17a0457f3688ef2a5893",
      "entries": 1
    },
    {
      "path": "Episode_2/DialogData.dv2",
      "size": 1146880,
      "sha256": "82d7a5973aa96190502f37babebfa73cc56ee8b042625912d0ba4a299b6639b4",
      "entries": 416
    },
    {
      "path": "Episode_2/Dialogs.dv2",
      "size": 303890432,
      "sha256": "626a433a74ee80211ccce1426868e1784dbdffbacb641975032ee30f76d73270",
      "entries": 1191
    },
    {
      "path": "Episode_2/InitSaveGame.dv2",
      "size": 622592,
      "sha256": "f209744f3a3a80a374561727baa29c0bf42975da78cd2332638805aa918d1822",
      "entries": 1
    },
    {
      "path": "FlyingFortresses.dv2",
      "size": 21069824,
      "sha256": "be25ffce7a54e89eeb80693dd423ed6c12e675955955727f6932d2b1442ab193",
      "entries": 42
    },
    {
      "path": "GFX.dv2",
      "size": 3735552,
      "sha256": "ed162752371d44370237365d89893b9ce255caed9dbbfef8ba9df8e7d7de5e81",
      "entries": 66
    },
    {
      "path": "GUI.dv2",
      "size": 14123008,
      "sha256": "e24de8b2a25c93e5d2d77459caae25d261a33525d4116a617994811c57845cc5",
      "entries": 259
    },
    {
      "path": "ItemPhysx.dv2",
      "size": 2424832,
      "sha256": "cfad3850433ce484e9df6dc605c7fd0263e29c3dd79232ed1fc1a7b4bda3b0af",
      "entries": 879
    },
    {
      "path": "Items.dv2",
      "size": 77365248,
      "sha256": "77e98dfab856f904c3d3612632bc40d10eb9403a5b41b4030f50b2c7cc3e8489",
      "entries": 886
    },
    {
      "path": "KFMs.dv2",
      "size": 98304,
      "sha256": "ca893320300aa00aa2440e4150f188f452664cb232d726025300efa571d7a59d",
      "entries": 121
    },
    {
      "path": "MainDataPlatform.dv2",
      "size": 458752,
      "sha256": "3d6ead338b3feb76ad7abc2b6a5358d93e286a3832833cfbea683eb6afd98c46",
      "entries": 25
    },
    {
      "path": "MainDataStartup.dv2",
      "size": 1376256,
      "sha256": "687a47918c211970839c9dca83c70c5ef346d14e40f679f55b6ada445f59a5d0",
      "entries": 265
    },
    {
      "path": "MainDataStreaming.dv2",
      "size": 4980736,
      "sha256": "9859e4d27f4766bbcd60f332b86548283843aff738505dcdead8a06ed4a53f4f",
      "entries": 3506
    },
    {
      "path": "MainDataStub.dv2",
      "size": 2555904,
      "sha256": "a065a79efc97ada09973973040d9abde50a5c7c33fae046ff216b0a43bc612ef",
      "entries": 427
    },
    {
      "path": "Patch.dv2",
      "size": 167739392,
      "sha256": "d393dad0cdc1c401f8de57104785fcc94a288c337ebcb428b5a44c275bf80c85",
      "entries": 696
    },
    {
      "path": "Scenery.dv2",
      "size": 305201152,
      "sha256": "7e474ef14c02408bdc516a7379313e0682186279419ce8132ea0efc8a6f73aa5",
      "entries": 1695
    },
    {
      "path": "SceneryPhysx.dv2",
      "size": 94273536,
      "sha256": "73f1ae196dd255eff66de07e2bbe2cdcc6172c6a7f8936d264b5c9c73f30a8d2",
      "entries": 2682
    },
    {
      "path": "Soundbanks.dv2",
      "size": 471957504,
      "sha256": "70a695851bedc562bbf5352fd63cc243ea6c48ec171f8d41aa6b6a74e81790a0",
      "entries": 223
    },
    {
      "path": "Textures.dv2",
      "size": 1683619840,
      "sha256": "812343a995a699ceb4ccd1661f7f1fff3463ea768c7bc58084e947ba8e0bd8a3",
      "entries": 5653
    },
    {
      "path": "Textures2.dv2",
      "size": 1220280320,
      "sha256": "9c5ce933a088424340859a340c49dfe9484516d442086b422dcf407978b0931c",
      "entries": 4382
    },
    {
      "path": "Trees.dv2",
      "size": 360448,
      "sha256": "2c75b108871fe0a7904026f888113255b4e38cc26b840c9e8e41696088108547",
      "entries": 108
    },
    {
      "path": "World/000_DreamScene/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "5e959acc40c39333733161f69091c949c5172d7f8afe2f7dde015e100428eac1",
      "entries": 14
    },
    {
      "path": "World/000_DreamScene/Main/003_Static.dv2",
      "size": 11829248,
      "sha256": "95f3ab0e73084b5bd5ca173dbcc9dc508d4c45478db59002f1116f97e735d356",
      "entries": 46
    },
    {
      "path": "World/000_DreamScene/Main/004_StaticMeshes.dv2",
      "size": 2097152,
      "sha256": "5bba1db5c4d96d4904860025685d7897489ffaa1e4f79623a4089621305f7d47",
      "entries": 1
    },
    {
      "path": "World/000_DreamScene/Main/005_Streamable.dv2",
      "size": 4915200,
      "sha256": "f7acab9515c2158e627edfffdca09cf542116980d50f61f60f7d08797d76c872",
      "entries": 51
    },
    {
      "path": "World/000_DreamScene/Main/006_StreamableInMemory.dv2",
      "size": 360448,
      "sha256": "a00149776335c328a37fbe32435b4ae2e35b216912a9a35f85d194e73157b716",
      "entries": 38
    },
    {
      "path": "World/001_BattleTower_Beach/Main/001_XMLs.dv2",
      "size": 131072,
      "sha256": "11ad93e150e880633394e74d6e10ed6a97f59f75e7c9339a066f4c2f8ac30ec7",
      "entries": 38
    },
    {
      "path": "World/001_BattleTower_Beach/Main/003_Static.dv2",
      "size": 11239424,
      "sha256": "e8d7e676d03618673c7384afc3d5c8019bed7b3d8c5ec1f656947dc0ed0dc20b",
      "entries": 71
    },
    {
      "path": "World/001_BattleTower_Beach/Main/004_StaticMeshes.dv2",
      "size": 4882432,
      "sha256": "11ce60bb71e479126d2c155c070b3df3d5121d06551c536fd92e1c16e187cd51",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Main/005_Streamable.dv2",
      "size": 7995392,
      "sha256": "7cc3996c9c4331edc9de0b27500f3bf95838c627ce95567a4a35c6406b475354",
      "entries": 69
    },
    {
      "path": "World/001_BattleTower_Beach/Main/006_StreamableInMemory.dv2",
      "size": 1048576,
      "sha256": "841606ec13c884082090a5ad6dd5d7673b209833613b79af67f882c1f1c85934",
      "entries": 182
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Choosing_Base/001_XMLs.dv2",
      "size": 98304,
      "sha256": "4ed3a7a72b1d2ae9f523568e2f916031657def0ec2a6259ebc8945403e980854",
      "entries": 31
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Choosing_Base/003_Static.dv2",
      "size": 753664,
      "sha256": "2e9672a34d218c67a863fe3ffe0a7e7c423d73a02e010eabadf8bdc70de9bbe2",
      "entries": 10
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Choosing_Base/004_StaticMeshes.dv2",
      "size": 4653056,
      "sha256": "f8a179d5d13d464e652a931109a5af8f45260eb4213bd32c3db927327d08219c",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Choosing_Base/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "c95be686635055b0e472fa6d02a7157e081652f2a0461a1de576e78640a1da4d",
      "entries": 11
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_DragonElf_Cave/001_XMLs.dv2",
      "size": 65536,
      "sha256": "8d1f6eafab36fc21f85f7d9f4899528b0ed2c11533e6bbd8d7a158ae17410122",
      "entries": 32
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_DragonElf_Cave/003_Static.dv2",
      "size": 229376,
      "sha256": "b36330f7ef6848aea630c3b8e114e5a4abead835f8b76579f318ba87ae9c0f4f",
      "entries": 11
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_DragonElf_Cave/004_StaticMeshes.dv2",
      "size": 884736,
      "sha256": "3c4cd47a25db60fc798ed6e134305a384dbbe65e361836df2d54225ca3f71529",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_DragonElf_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "b2f6352b592f485b7b4787fd1a494318fb4532dd52abe519fa6e48a3d9fa2dc5",
      "entries": 11
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Abandoned_Study_Cave/001_XMLs.dv2",
      "size": 65536,
      "sha256": "f821be3471acce2efcd521a78fec19559bef911fd2833b2b5b46cece348f113d",
      "entries": 31
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Abandoned_Study_Cave/003_Static.dv2",
      "size": 229376,
      "sha256": "88d4dd3c9d91d6b90a1a9968f5d682759399d3d7f496628a627053a7895a17ac",
      "entries": 9
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Abandoned_Study_Cave/004_StaticMeshes.dv2",
      "size": 1441792,
      "sha256": "ef07ddf3794495c15b8667db22f00e00126aacbf464d505d26df2f2422c03fbc",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Abandoned_Study_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "46d3b4365dd9a1ec0cb93a4d0c55ab7e5cf1b7c5cd1c2ad946aef18c69cfb2ab",
      "entries": 11
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Elevator_Cave/001_XMLs.dv2",
      "size": 98304,
      "sha256": "529278cf950d85f755ad543c67cc4bb0b4aa3ee26e7694e31f3fbf5f46a42a3c",
      "entries": 32
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Elevator_Cave/003_Static.dv2",
      "size": 1212416,
      "sha256": "d12e676f96bb1bed60a6a4a3446403b82b94099673b6560c16316cb54d3ec408",
      "entries": 10
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Elevator_Cave/004_StaticMeshes.dv2",
      "size": 6455296,
      "sha256": "328b6c1906b1b10cda4264ab5e1fe2acb19bfd0ef2a8d69a565d568829811651",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTB_Laiken_Elevator_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "b27c3ce9526c151127bc24e4f4a917ac90a8f561b611ebccc145e9f3d189bbae",
      "entries": 11
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_BattleTower/001_XMLs.dv2",
      "size": 98304,
      "sha256": "bb67c2b87389ee3ae279a1f055fbaad6f32a1003ff3f04713c01b4293df21d10",
      "entries": 36
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_BattleTower/003_Static.dv2",
      "size": 2981888,
      "sha256": "1824a2d839d47677bdda1dcb9696a8729bebeefa621c64704745373f5675478a",
      "entries": 35
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_BattleTower/004_StaticMeshes.dv2",
      "size": 2916352,
      "sha256": "28f5ca6fa21e688fd83be818afec647a2b04006e934971176a9b2d224c3816e9",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_BattleTower/005_Streamable.dv2",
      "size": 917504,
      "sha256": "163212a42162eae78fa4f3f5e8c8779781fd3708bf1dfe2c195d994d9652bf77",
      "entries": 6
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_BattleTower/006_StreamableInMemory.dv2",
      "size": 917504,
      "sha256": "3f7863633e27bb94c2fc4ef7da9b2e9b8312f5715fcf398973b51091146e6bce",
      "entries": 99
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_TrophyRoom/001_XMLs.dv2",
      "size": 98304,
      "sha256": "debfe91fa1041d63b504d0140888fde9d9013b6ec0a388520467dc0f62cff0cd",
      "entries": 31
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_TrophyRoom/003_Static.dv2",
      "size": 884736,
      "sha256": "a74580dbea18bf2551518d2b1483b3ae9f326bade6df1d3f1c04d272434171f6",
      "entries": 10
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_TrophyRoom/004_StaticMeshes.dv2",
      "size": 7143424,
      "sha256": "e7b1560ac2834972295a409d3fb2cb62d0072366b347b1e2a52daf663568707a",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach/Subregions/BTI_Interior_TrophyRoom/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "b897e8fdb16e03558f3845ecec9922389885b9ff172fed57724e5ae5ee6bbcda",
      "entries": 18
    },
    {
      "path": "World/001_BattleTower_Beach_2/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "a386b13d69d5dadc1dfdf7d824e81c6891c37676397891592ac8752ff0f624e5",
      "entries": 16
    },
    {
      "path": "World/001_BattleTower_Beach_2/Main/003_Static.dv2",
      "size": 6094848,
      "sha256": "08ea0e8a61d43791c9a4423c9aef1fad5ee8538c3a4cc120a130dc6cd3d948dd",
      "entries": 40
    },
    {
      "path": "World/001_BattleTower_Beach_2/Main/004_StaticMeshes.dv2",
      "size": 5341184,
      "sha256": "2c59944deb2effd026036189f5d68a3c5a0794a4152b6558beecc72b99608cff",
      "entries": 1
    },
    {
      "path": "World/001_BattleTower_Beach_2/Main/005_Streamable.dv2",
      "size": 6422528,
      "sha256": "2b68fb56df0f7d70b30636d0c118888c37619549f81a4e625321c0f3c95b510d",
      "entries": 38
    },
    {
      "path": "World/001_BattleTower_Beach_2/Main/006_StreamableInMemory.dv2",
      "size": 163840,
      "sha256": "d931d32e970a23498b450d9b2b9edf623a78d579a432b336444baf5e1945ad5d",
      "entries": 28
    },
    {
      "path": "World/003_Aleroth_City/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "672c7f9a2bae08f58c3dff021a5e3ef4b28e4b0b2060b4fd69eef126315bd7bc",
      "entries": 19
    },
    {
      "path": "World/003_Aleroth_City/Main/003_Static.dv2",
      "size": 3637248,
      "sha256": "08292477206c2f9c9ad008a39cdaadfb99f1e5f94ced1ffcaa81c86bf488626e",
      "entries": 82
    },
    {
      "path": "World/003_Aleroth_City/Main/004_StaticMeshes.dv2",
      "size": 40402944,
      "sha256": "e56b88a268861918da0120748c35b27f12c475585c7579ebd33107f80ce81627",
      "entries": 1
    },
    {
      "path": "World/003_Aleroth_City/Main/005_Streamable.dv2",
      "size": 2195456,
      "sha256": "426ddd0099c0c9bd86a7e756dcd631b827ea0ed7ad258a4917632649e8b51871",
      "entries": 62
    },
    {
      "path": "World/003_Aleroth_City/Main/006_StreamableInMemory.dv2",
      "size": 1441792,
      "sha256": "915a1a124464530b22756d3959cf09636a5330f0e5481f9b3f4c584a6640031f",
      "entries": 155
    },
    {
      "path": "World/003_Aleroth_City/Subregions/AL_Waitingroom_INT/001_XMLs.dv2",
      "size": 65536,
      "sha256": "7750399cab42d21bda99e6bb611d591cf36921727298619b8b2e99131530d5e3",
      "entries": 12
    },
    {
      "path": "World/003_Aleroth_City/Subregions/AL_Waitingroom_INT/003_Static.dv2",
      "size": 655360,
      "sha256": "c155270021b215f65885be1072dfbccaf5f5f3fed15115c6201fd5ec55cdd016",
      "entries": 11
    },
    {
      "path": "World/003_Aleroth_City/Subregions/AL_Waitingroom_INT/004_StaticMeshes.dv2",
      "size": 7274496,
      "sha256": "6d20ab6eb8ec4192b8ac253eed56d3074f51dc8f11b97bcf5bc07280a8bf9149",
      "entries": 1
    },
    {
      "path": "World/003_Aleroth_City/Subregions/AL_Waitingroom_INT/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "6f60b24aea7d23b70d03f78b375c1e3628a054c5347eb062df95168345e9af6b",
      "entries": 11
    },
    {
      "path": "World/004_Tutorial/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "e9da9786acf93dc8b36dd20fdbebaae4e82dacb6228840aea9345c3fc5a90875",
      "entries": 17
    },
    {
      "path": "World/004_Tutorial/Main/003_Static.dv2",
      "size": 4685824,
      "sha256": "ac440aaeca8a48af9922a2919c4be6ff66d2bfdce33118ee3b3ff8d4c9ce07bb",
      "entries": 31
    },
    {
      "path": "World/004_Tutorial/Main/004_StaticMeshes.dv2",
      "size": 6258688,
      "sha256": "4400f400c89fa29058ad9279d687f9ba646c8e5d5f4bf505fa7c250825bd6dd4",
      "entries": 1
    },
    {
      "path": "World/004_Tutorial/Main/005_Streamable.dv2",
      "size": 1998848,
      "sha256": "82e2cb05e94592c3efcdda7b86e75e71ae00c0918913f6df3638ee6281b9ccc3",
      "entries": 14
    },
    {
      "path": "World/004_Tutorial/Main/006_StreamableInMemory.dv2",
      "size": 262144,
      "sha256": "e8795d17106af485780741f9085e6209675c3741c00a61972ac0321143ceff05",
      "entries": 71
    },
    {
      "path": "World/006_BrokenValley_3/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "e733dd10efa20c86753eae8181247bda1c48a46328887b7f1d1e87802aadbcf5",
      "entries": 19
    },
    {
      "path": "World/006_BrokenValley_3/Main/003_Static.dv2",
      "size": 9371648,
      "sha256": "e4a6fede61b19456da2513a67a2e25c473c8cd5471807dde999410bddfe7f384",
      "entries": 88
    },
    {
      "path": "World/006_BrokenValley_3/Main/004_StaticMeshes.dv2",
      "size": 9895936,
      "sha256": "84a1b85a99ab1ae8a81f0c8f12d9b2d89379e7a217fec8edbed03d1cfa5b5032",
      "entries": 1
    },
    {
      "path": "World/006_BrokenValley_3/Main/005_Streamable.dv2",
      "size": 19300352,
      "sha256": "d0304656b6ed15f851942835dc092685757cedb58ac21b0c08234bc363260124",
      "entries": 114
    },
    {
      "path": "World/006_BrokenValley_3/Main/006_StreamableInMemory.dv2",
      "size": 360448,
      "sha256": "e08acef4379b1324c1a40e82c21f6baebe2cb9bae7bdb84c38750cc1c45e12f4",
      "entries": 80
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Geshniz/001_XMLs.dv2",
      "size": 32768,
      "sha256": "fbf59b88d742824d8453fb2f16ec6d09adb7be46d2616149362044d834e09dc7",
      "entries": 14
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Geshniz/003_Static.dv2",
      "size": 655360,
      "sha256": "e660fa6cf9466c01d84e48d3d7deda03fc219c861956dd630cfde88157f4e856",
      "entries": 10
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Geshniz/004_StaticMeshes.dv2",
      "size": 1146880,
      "sha256": "f2260a9050954c8aba629f62a927f6190a8a65f46d0f07a6eed496c6da4c7057",
      "entries": 1
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Geshniz/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "49db0d2ba0e13215e8991875bd506d62bd2c33ec1b3e98c1d857e6e6a1c513b8",
      "entries": 12
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Rayhun/001_XMLs.dv2",
      "size": 32768,
      "sha256": "133147a7e593b422480fc77857a679df2056c07d67fd70587c969781e3d8e2ea",
      "entries": 14
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Rayhun/003_Static.dv2",
      "size": 688128,
      "sha256": "8c0681f310e98443ded9560e9dde71186a242c602178cadee0780e07ff156e0a",
      "entries": 10
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Rayhun/004_StaticMeshes.dv2",
      "size": 1835008,
      "sha256": "37dd063471d5b2ab88a97c50fe57250e9d8e787c5634ab7f08ed5f3cadcd24b5",
      "entries": 1
    },
    {
      "path": "World/006_BrokenValley_3/Subregions/BV3_Rayhun/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "d3834ac30143ec509952b610c86da782ffe87d53dfad435736ed393ebd2faec7",
      "entries": 12
    },
    {
      "path": "World/AstralPlane/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "98de637a9d800abbc8149391f0e0025a65807f7387a199edc506d2a4c7d2b177",
      "entries": 8
    },
    {
      "path": "World/AstralPlane/Main/003_Static.dv2",
      "size": 2588672,
      "sha256": "2d616fccd1a7af799677f0e25f3bcbd02e7501a496a1179b93864205af215a81",
      "entries": 34
    },
    {
      "path": "World/AstralPlane/Main/004_StaticMeshes.dv2",
      "size": 3506176,
      "sha256": "05f04befad02485a2932d1b0dfc56462a7d87c0274896a97cb613378cda35b2c",
      "entries": 1
    },
    {
      "path": "World/AstralPlane/Main/005_Streamable.dv2",
      "size": 3178496,
      "sha256": "7a8229ce9b23e344b63ff4f645cbee31c6f6620a14ba5a27e988fcbe64a54804",
      "entries": 16
    },
    {
      "path": "World/AstralPlane/Main/006_StreamableInMemory.dv2",
      "size": 163840,
      "sha256": "74350ab9dbf412b175a1d07d786da7834b237a75f4203bb2272bb424b4f84681",
      "entries": 26
    },
    {
      "path": "World/Banditcamp/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "2f9d6a4aeed5b297818ff77d8860c6d524e25fd5e9b4953e5ec210024058f5a0",
      "entries": 18
    },
    {
      "path": "World/Banditcamp/Main/003_Static.dv2",
      "size": 10715136,
      "sha256": "c9c49fdac65a75a4afd420cab1f3c422f6b32780c276544d589143a879205726",
      "entries": 75
    },
    {
      "path": "World/Banditcamp/Main/004_StaticMeshes.dv2",
      "size": 6750208,
      "sha256": "28027e860d4acb8b7e0149153619aee6364923187672f82f377faea17d512022",
      "entries": 1
    },
    {
      "path": "World/Banditcamp/Main/005_Streamable.dv2",
      "size": 3932160,
      "sha256": "f7f4e3c19c193da502033c22beece8eb26b9d059144960fa22a9da1c58803979",
      "entries": 21
    },
    {
      "path": "World/Banditcamp/Main/006_StreamableInMemory.dv2",
      "size": 425984,
      "sha256": "af5231ea090fa834ae8418d5151b5d26f81062978382f95ae9b98b138ffe116d",
      "entries": 148
    },
    {
      "path": "World/Banditcamp/Subregions/BanditCamp_Cave/001_XMLs.dv2",
      "size": 32768,
      "sha256": "eefe3a49be9b9c37868c380abdd35459d3973790db5979dc57dd75c1156ed673",
      "entries": 14
    },
    {
      "path": "World/Banditcamp/Subregions/BanditCamp_Cave/003_Static.dv2",
      "size": 294912,
      "sha256": "8d85577d2029331190caf6e4b21932bc87fce7e8e3f94324210edd1630416055",
      "entries": 9
    },
    {
      "path": "World/Banditcamp/Subregions/BanditCamp_Cave/004_StaticMeshes.dv2",
      "size": 1310720,
      "sha256": "1151a3043ec8f4c8944c3daa5d18d1d9a5518ec22cab5faf874c2ffabade085b",
      "entries": 1
    },
    {
      "path": "World/Banditcamp/Subregions/BanditCamp_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "abdc1093b59af5a02f01241162e051140b6ed5c1d7bd6f31869bc88dbe10051b",
      "entries": 13
    },
    {
      "path": "World/BrokenValley_2/Main/001_XMLs.dv2",
      "size": 294912,
      "sha256": "2b60f43dc89809a35d4e4ab8e55854ff0182fda7bcbdc521bf06f7c14c7d365a",
      "entries": 66
    },
    {
      "path": "World/BrokenValley_2/Main/003_Static.dv2",
      "size": 10485760,
      "sha256": "3226c2b6d0f8aa7027cfefe56e7c3d3d5b1a3bf2012f3adf787fd2b579050c09",
      "entries": 92
    },
    {
      "path": "World/BrokenValley_2/Main/004_StaticMeshes.dv2",
      "size": 13762560,
      "sha256": "933da725ed18f31914e0fabc64ffbc47372c054f37952839cc9045ef16f64c33",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Main/005_Streamable.dv2",
      "size": 16154624,
      "sha256": "fd6ce904572f4406472662b6daddc0c3e6202ae559dae73a5141fe911fb5a144",
      "entries": 72
    },
    {
      "path": "World/BrokenValley_2/Main/006_StreamableInMemory.dv2",
      "size": 1441792,
      "sha256": "14b5939d0dbe5149f1f149ed1f556dbbfcf65c9d793da4a944dafa004cdd0344",
      "entries": 639
    },
    {
      "path": "World/BrokenValley_2/Subregions/Arben_Tomb/001_XMLs.dv2",
      "size": 196608,
      "sha256": "23f4224ec6ae15d57b795211ed5fd6ce6c87401967ba9cd828b01f40da6e93a9",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/Arben_Tomb/003_Static.dv2",
      "size": 360448,
      "sha256": "84aeda4d83bfc12ca748bc88cabe9830e1ae462480f0c02d365214cb1a2994b7",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Arben_Tomb/004_StaticMeshes.dv2",
      "size": 2064384,
      "sha256": "0c4206b0628a92b1a7b00707fb5142cc35353744dfd7f3135ddd2cc2e09088a2",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Arben_Tomb/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "102d8829efd7cf66ec3fd5d9b7dacc3cc99abc855e6a56b8d134d05b64bbd082",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Barracks/001_XMLs.dv2",
      "size": 196608,
      "sha256": "c6a173950134c7b1f26cb16a209094e63af19e31fbfe97bdee8626d17561639a",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/Barracks/003_Static.dv2",
      "size": 622592,
      "sha256": "be6464e268d1f8a3593102fbd3a093c2dc1bcde20882af887fa21f2673485792",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Barracks/004_StaticMeshes.dv2",
      "size": 1245184,
      "sha256": "23eabc8417ad1fc20787ac8cf5b1658cb659ab8736970b5bd9b12f8cc62d4a94",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Barracks/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "80bcb9af5d9271d4a1b568b0c6be2fb6036728a326084d736829bc06eacb1d46",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Blacksmith/001_XMLs.dv2",
      "size": 196608,
      "sha256": "560852bbd43a764106b07d059087f24c57e69ec050cd4047212a90c340c56658",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Blacksmith/003_Static.dv2",
      "size": 98304,
      "sha256": "6981003c9fd9cf25a4792d16565621c65b14a8520d8a5cc752536c6e7a21563a",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/Blacksmith/004_StaticMeshes.dv2",
      "size": 294912,
      "sha256": "e6ebb707209d8220d614388a2f85c91a9233d750310178f7989be19d33a2c022",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Blacksmith/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "62a95d8d973496058c6c6eb1b8ef0e8e2e8a69a5c3642123b373b76ca989f424",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Basement_Blacksmith/001_XMLs.dv2",
      "size": 196608,
      "sha256": "2defbf8b45ea427f40b5bd4e0cbb02a3018079cb87c5ade436215ec2f69583a7",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Basement_Blacksmith/003_Static.dv2",
      "size": 98304,
      "sha256": "511425fb79229912bc22365d0826e1c188fb65138f1f11a1c114154f8926afcd",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Basement_Blacksmith/004_StaticMeshes.dv2",
      "size": 196608,
      "sha256": "5093b75724818315b1f1645af9ebf82e9e9fd8d3ef6abd5af979c12935f31f42",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Basement_Blacksmith/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "b454454a7968f7874aeda16d9434818fbe319a812b486b483a123960939e5ca5",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Cave_B_SecretPassage/001_XMLs.dv2",
      "size": 196608,
      "sha256": "f1f12a2d3a301a2e0900ff4ea8f87d67dcf67eef0cba7c0bdceb671dfa61ca93",
      "entries": 60
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Cave_B_SecretPassage/003_Static.dv2",
      "size": 983040,
      "sha256": "03da84b36c9a9ae63be6f809b0030b02d77f60ee9cbfa200bf71806cc70b137c",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Cave_B_SecretPassage/004_StaticMeshes.dv2",
      "size": 4128768,
      "sha256": "0cd6c6ad8e4a3de147597db6c3b8ed519f09d6d4bd8211d0bdc33b1d598a1032",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Cave_B_SecretPassage/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "c6befe7f8b3799d429353b766883e3fde15808131728c50b41e43fcc31e39fe4",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Chapel/001_XMLs.dv2",
      "size": 196608,
      "sha256": "5d6d327ba857c56cf5a85b66c150a7d2c030809abfae44114bd6818146912e47",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Chapel/003_Static.dv2",
      "size": 327680,
      "sha256": "aff0813b06cf47da585ed5d80eddea080d95175037bf7406c134c4cfff268eed",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Chapel/004_StaticMeshes.dv2",
      "size": 1966080,
      "sha256": "333d621e972887f6ce588620da4eff45c3857cc611e07cf29f420f304bddc902",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Chapel/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "4eadb9a618153e4c364b98aed414e8396bbe837b1058deaafd125b642d0e0c20",
      "entries": 13
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Creature_Cave/001_XMLs.dv2",
      "size": 196608,
      "sha256": "a8ce03c030cea9bf284e1cfabdcec2d002c7d064eb9435a424d8ef10cf540b9f",
      "entries": 60
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Creature_Cave/003_Static.dv2",
      "size": 622592,
      "sha256": "c2b4cf930a6c8e35a7c013736c1d6d9ab6157c8603681de4d267fc7ee21cc56e",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Creature_Cave/004_StaticMeshes.dv2",
      "size": 4063232,
      "sha256": "2a58b6403dd4609f18db9ae9057f0f99cfdea9d3d478fd2ce6efdafe09660eff",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Creature_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "b9edf1e70ac3d025ca45df2e9a90b8492e8f6c98be0bc980eb616b8bce79fa25",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Dungeon_A/001_XMLs.dv2",
      "size": 196608,
      "sha256": "9a4659589fbc4ec842ad2c015b95aeaa5ae63bbb57f2d9456a2d6cff0db2ccbc",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Dungeon_A/003_Static.dv2",
      "size": 196608,
      "sha256": "9db01927d6a08fb6044269a79ad6204086052fab9c08e6259bd995df8cdfdfba",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Dungeon_A/004_StaticMeshes.dv2",
      "size": 1048576,
      "sha256": "4ba99714764339200d7f78d220e6c6865e56414c3510c10e6a6b557ebe0fe2f0",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Dungeon_A/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "5a836f7e353cd67e8c51aef659c64fe3b4a995961f0c4a1cfc06b4fc9e316a52",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Hidden_Cave_3_Exits_2/001_XMLs.dv2",
      "size": 229376,
      "sha256": "859430bf51077cd83aa0f48511f506e454b01efc1cf6ab3a6822c81e32382b8c",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Hidden_Cave_3_Exits_2/003_Static.dv2",
      "size": 1048576,
      "sha256": "2e63ca7f688f1e170413f3c1bf0aa0197d462ce8e39b18fa8cd4b883c0841f5e",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Hidden_Cave_3_Exits_2/004_StaticMeshes.dv2",
      "size": 6488064,
      "sha256": "37d714508b187f43463d0e140a2c4a760cd8a53452dc047fb6c1ceefb86551fd",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Hidden_Cave_3_Exits_2/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "3059c31d9f1b1bda144fa13af8d0024dd59cd8ecb6ef64b3eece45f8d52fa13c",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Miller_Alchemy_Cave/001_XMLs.dv2",
      "size": 196608,
      "sha256": "4df78cd8f02b3144dbcd7ab8830caa86f4bda8e08908afe98cc1226f0fb779a2",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Miller_Alchemy_Cave/003_Static.dv2",
      "size": 229376,
      "sha256": "8342ac81e05f69f32e1b5771c4d1b159bfc925c022f9b9184ecd3dfd95ecc16c",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Miller_Alchemy_Cave/004_StaticMeshes.dv2",
      "size": 1802240,
      "sha256": "c5456614a96db6bbd8e9e5c540b01b7d8520f87bf7fe8f4587a8ae23ea56f246",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Miller_Alchemy_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "812000889a9cc357431253779fb6e2dd098c68e303a8c994e2bedfe0161e1942",
      "entries": 11
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cave/001_XMLs.dv2",
      "size": 196608,
      "sha256": "6b02e095abeb321669b486b65488cf5b342f42eebdb83b11d2976dbd0dbf60d1",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cave/003_Static.dv2",
      "size": 163840,
      "sha256": "446e73dc7f886f1abcb22f8f7922f5a61075e7ea3a60a5a3b404f63a0370795a",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cave/004_StaticMeshes.dv2",
      "size": 917504,
      "sha256": "e9bfe74b3010245eacc65b8f7e0418fc9c138f9141661eed37c91c0dfbd9bb2e",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "9fa50da09f19252447622c6bd5214db57f1f8a648342f69e9ca56d828d2152a4",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cellar/001_XMLs.dv2",
      "size": 196608,
      "sha256": "49e0228be08690befaf78e8c191922bbb3d7b5aea504b13e35d3db47c45bcc0b",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cellar/003_Static.dv2",
      "size": 131072,
      "sha256": "37b751c252818888fd359e09b378baa5c82dead36362167f2efd06b3aaef6856",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cellar/004_StaticMeshes.dv2",
      "size": 589824,
      "sha256": "21888a1e6c776333d40c7b8123ae86a23f3d605bb7ebdd4541fbdfc695f936f8",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_1_Cellar/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "a18e3a8e9a66bcfa4d143efe21f7ea07a512be372533ee37ec98d8702ac26962",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cave/001_XMLs.dv2",
      "size": 196608,
      "sha256": "71c61b9264e4561a06b7355f1b9534461dcb932ff756d98d073ed2657c680bff",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cave/003_Static.dv2",
      "size": 131072,
      "sha256": "6cfdf2492d5070e7101f8c8eb9cad16de20f7cde2931c8007ee71f9232f40c45",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cave/004_StaticMeshes.dv2",
      "size": 917504,
      "sha256": "c1fab8075bb53c3b0441a1ea6823a6ee0a33126182667108bdd054a752c23b51",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "e7dc0dc4ac59b142edcb19cdca253bdf679f61bb922d48eeb78b552d70de0968",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cellar/001_XMLs.dv2",
      "size": 196608,
      "sha256": "0ffe14cffeafc7579700e2bbc7b98d677bf3c82a1f737702663af6ac6b60aa14",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cellar/003_Static.dv2",
      "size": 65536,
      "sha256": "1c4acdc10d6d041c712af6951a4603d38f42f17f0c582855cb461c0dabdc7786",
      "entries": 3
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cellar/004_StaticMeshes.dv2",
      "size": 589824,
      "sha256": "0c39f46491190fc1daa4235222c4e69db39ab68ec7401f4f1e34ef339595eaae",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_2_Cellar/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "0a1e14187575e7b78ab2f9dfb99563b41ccefffaf5fabfb669959b6236ae6695",
      "entries": 6
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_3_Cave/001_XMLs.dv2",
      "size": 196608,
      "sha256": "a3cd1d95dbcfd04c971232f49bc140579973600f4e1fc454851f2f2c0c3f9831",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_3_Cave/003_Static.dv2",
      "size": 229376,
      "sha256": "2891c37bb7d627e21a021cc952722475b9cafb124be7b97001992ad99d779faf",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_3_Cave/004_StaticMeshes.dv2",
      "size": 360448,
      "sha256": "040a694f46767926ce99a33affe0ea21d076ccc64a2c84f7e6b6c549bb178ddc",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mindread_3_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "6fc895c5791ea1c04fca628239d8841a647b104ae360ea4ac07f3f8c30a91a15",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mine_Cave_v2/001_XMLs.dv2",
      "size": 196608,
      "sha256": "e7cdef806e8918bcb761050bdc432427114bdf91603942486f2773fb595fe8b7",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mine_Cave_v2/003_Static.dv2",
      "size": 1081344,
      "sha256": "7a5dd8539dda10606b317416e89eb096a838148201b584bfd2cabe45834887b9",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mine_Cave_v2/004_StaticMeshes.dv2",
      "size": 11141120,
      "sha256": "ece6dc366609018d60a2309044690f6a277235ab5561cf59c54ddd26926ae4f3",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Mine_Cave_v2/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "c8bcf68a0d6468b6a3a9bac90cce7ad263702d3957cd9f339e84f1c0d9c14b4f",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Necromander_Platform/001_XMLs.dv2",
      "size": 196608,
      "sha256": "b05546ed286418c20152708ff1cb815811f003aacbdb25685cd6ef78d2a0396c",
      "entries": 60
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Necromander_Platform/003_Static.dv2",
      "size": 458752,
      "sha256": "e25259932a2863ef4010bf7a4017d4dbf86756feb37b59b28e54bd6851dc8eb9",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Necromander_Platform/004_StaticMeshes.dv2",
      "size": 1966080,
      "sha256": "ccb24bbca605adf62d9b7689b30d8cda273bbb87acbc0c7eb06236d12549685e",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Necromander_Platform/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "869f7e6baf6995396fa6ccd8b95af1dcf6d84bbb2e0c512cba07ef4974030cc8",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Rashida/001_XMLs.dv2",
      "size": 196608,
      "sha256": "08e3bdc638d477adefc83a37550dc94fe3b97e9cc0d6f1cb4f36b91b8bbfa188",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Rashida/003_Static.dv2",
      "size": 65536,
      "sha256": "0987d3f5f7de29c40d288aa42c315bd31b2851071b15ab9e11cd17e223c258ae",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Rashida/004_StaticMeshes.dv2",
      "size": 229376,
      "sha256": "8dc4a6172c77ed9295b09f94e5c8cd61c75f48cf73aad07f64aa6343e7c96b71",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_Rashida/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "500e5b6c5e92197d15d320292beb33493a1a41c8c0d9deb36fb53b57494788d4",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_SecretDungeon_01/001_XMLs.dv2",
      "size": 196608,
      "sha256": "653e103bac8ab0b77b9ed74936c24f356909ed59c693efa6117c0c2ba70b0d65",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_SecretDungeon_01/003_Static.dv2",
      "size": 458752,
      "sha256": "e79552bcec4ebf12db1dbc7c5cc6e5730744f02ddb7c2bc7a93b546318f99426",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_SecretDungeon_01/004_StaticMeshes.dv2",
      "size": 2523136,
      "sha256": "a64a5066278429a8eb5eee1a08a84783960b195ce42c0f06d269fcb32b78f298",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/BV_SecretDungeon_01/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "9b33a3dbbc344b92d8950a0e4f08211017adc83cb4783ccbc0fba81823d62bbe",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Chapel/001_XMLs.dv2",
      "size": 196608,
      "sha256": "2796f375c01a9a62cf715a78d8b554689859ffc7ce7051852e101c135423361c",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Chapel/003_Static.dv2",
      "size": 425984,
      "sha256": "b698cc5c6ffc69389385f39fe8cd6dc9d8942842eb282869d791cd4cc919cc8c",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Chapel/004_StaticMeshes.dv2",
      "size": 1638400,
      "sha256": "a9d51588d1dce12ea8ead043e1d3265e834c434f970e597c99a8f9c28cf17dc2",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Chapel/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "1739148f8ab0ad68b2eaa45500d83b686f67092df75332821a90259bbadc6daf",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Farm_A/001_XMLs.dv2",
      "size": 196608,
      "sha256": "b8268c5894c1586922e2db826e92074953e4f52f1e52546ef809b2b6e7490999",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Farm_A/003_Static.dv2",
      "size": 98304,
      "sha256": "f0d870012ccfa13188116fcf256ab0a95632ae570b1f8d70b76d3ab95b9facc0",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/Farm_A/004_StaticMeshes.dv2",
      "size": 393216,
      "sha256": "cfa02b67b873aa9dea61de47360db329c0afa5a5b050b584f8542b6e731c9dd5",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Farm_A/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "3a40143649fbd0207ca45ea23b73a33fa5a048351417c07397da5b6fe4182633",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Jackson_Cellar/001_XMLs.dv2",
      "size": 196608,
      "sha256": "d10f34f309d87f24d4fe4453f96cd9120cc9f671715483f44db7161f71504603",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Jackson_Cellar/003_Static.dv2",
      "size": 131072,
      "sha256": "9545c430e258f279015d0b15061a8c6f5d13fb97332866e2dbd8a72f3ca5f64f",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/Jackson_Cellar/004_StaticMeshes.dv2",
      "size": 196608,
      "sha256": "1752062ab77f666d77920b6accbe1f75acc04554fa7e51e9ffd0c4c784f6209c",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Jackson_Cellar/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "09849dd5dfbf36f23f864ad4fdc87d94269ce332288458fe3201dd57c972e6a9",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Armory/001_XMLs.dv2",
      "size": 196608,
      "sha256": "7856134e153793f34d0cd71053a366f9af4439b41c46cdd4158aed147cce99f9",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Armory/003_Static.dv2",
      "size": 229376,
      "sha256": "90e1b3b21c7255c361473c38fdf074993f8b3f4c9663965d0afa9618051cee35",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Armory/004_StaticMeshes.dv2",
      "size": 1146880,
      "sha256": "a3bfd753ef7bd6acce6c376a31d96a1dd1bb834368afae586d2f135fceee6f9f",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Armory/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "660ef6dff55df28ddb8612072970c2fe54b9560e4580376dffefceb1f08ec130",
      "entries": 11
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Chambers/001_XMLs.dv2",
      "size": 196608,
      "sha256": "4b52756ba6a5e99fb40f514d9d9c00d8fa91f1ced9d7c90ebe16d72dfd3ebae5",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Chambers/003_Static.dv2",
      "size": 262144,
      "sha256": "b4b46e22984a251fe5c91db09530c416738d6cbdfa008d766acedab8f235e3d4",
      "entries": 9
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Chambers/004_StaticMeshes.dv2",
      "size": 3244032,
      "sha256": "2ad55bedcf25af43a5a764f628d45ba8123e6117c17f1745c81ad07fe6793a27",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Chambers/006_StreamableInMemory.dv2",
      "size": 98304,
      "sha256": "5334b79ca014838ee9f6e09703a8d4600b46c584fa75f840f3b9208990280b2f",
      "entries": 77
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Dungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "2029e3b9038244d4f0a228dd518898c6587a7486deaaff4556c98e11f5816834",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Dungeon/003_Static.dv2",
      "size": 229376,
      "sha256": "aca22b0c3847eeab563eef98aba40819fca9e40ccd55edc6addde336ae419836",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Dungeon/004_StaticMeshes.dv2",
      "size": 2293760,
      "sha256": "745a39afff0285c4ef508830090f89a3b233cbe80fa30792c5f0e0a09652e41b",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Lovis_Dungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "a3940acc71b63db020b6c201885fd4e897345f061c25526ed786983d8cef9707",
      "entries": 11
    },
    {
      "path": "World/BrokenValley_2/Subregions/MineEntrance/001_XMLs.dv2",
      "size": 196608,
      "sha256": "8e0f21f35f4234c0f9de5273b6f34d19cfbcb699a4aa14e383823340a182d46f",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/MineEntrance/003_Static.dv2",
      "size": 425984,
      "sha256": "23b739eff128cb52cf8f66682f38847c270966a47a63df3f97ca4b2e6b581dd2",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/MineEntrance/004_StaticMeshes.dv2",
      "size": 1343488,
      "sha256": "33c8236089dd34ec25d930bde0650449c22719fe8c87c20d0d88d2c292109a32",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/MineEntrance/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "89783e072d1bfc59f378d02fc42d4d0782cf34e513898d206ce3da2d28136921",
      "entries": 11
    },
    {
      "path": "World/BrokenValley_2/Subregions/Piggyfarm/001_XMLs.dv2",
      "size": 196608,
      "sha256": "37d55cf93cc7357d322cff11463cd7eb727af81dc8836a088cd2dcea738d8d3b",
      "entries": 58
    },
    {
      "path": "World/BrokenValley_2/Subregions/Piggyfarm/003_Static.dv2",
      "size": 229376,
      "sha256": "cb0d47e5aa72db8cae732e4f99d9948ed33eaba5ca070cfc78548c7550309677",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Piggyfarm/004_StaticMeshes.dv2",
      "size": 294912,
      "sha256": "9c3593a3018010c63f155d62ed48c19085fafba80b5971f6669c3c3ee5a63b86",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Piggyfarm/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "53c0a4ffb510e33c35612ddcdf0164d15b17c4c36346b66658befcf81f24e11e",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Tavern/001_XMLs.dv2",
      "size": 196608,
      "sha256": "463f6d81fef451e751c1e5844eec92e19cacbcdf3480fe7d3ca0747a5beb46fd",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/Tavern/003_Static.dv2",
      "size": 1310720,
      "sha256": "5da57200a22553bbaab661ca94d63f9f5fc61174e8ea61fc54c9d0c851ae29d3",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Tavern/004_StaticMeshes.dv2",
      "size": 3440640,
      "sha256": "c6f2eb923045491adaedbb2cc7fce770296cbac2cbf1eee0e41d694a69fbc156",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Tavern/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "a2212a4e116b812b583bd10b4137af641ab2e69fa4d8c068751d1dbe09d984d3",
      "entries": 12
    },
    {
      "path": "World/BrokenValley_2/Subregions/Watermill/001_XMLs.dv2",
      "size": 196608,
      "sha256": "20de70666800f9c11dbfaca3606dadadc2c597869421c7aa139db26005a1ac96",
      "entries": 59
    },
    {
      "path": "World/BrokenValley_2/Subregions/Watermill/003_Static.dv2",
      "size": 491520,
      "sha256": "869a11520691de4c64f8c009d0d65279a669b48adcc3058d897d677bea747303",
      "entries": 10
    },
    {
      "path": "World/BrokenValley_2/Subregions/Watermill/004_StaticMeshes.dv2",
      "size": 1277952,
      "sha256": "42d02a1d90fd24bcf839f3c7c78c5fd674929c3e18a26259e883871818c58cc8",
      "entries": 1
    },
    {
      "path": "World/BrokenValley_2/Subregions/Watermill/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "d1dce11e44aefcddd716f2ec842b23b2a8b1dabc9159f3cc17056bf236735c5e",
      "entries": 11
    },
    {
      "path": "World/Damians_Fortress_1/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "6c97981e9cf68b1b231c1b4b25c410ddf3224a01000b351f31c2c8197350e4cb",
      "entries": 21
    },
    {
      "path": "World/Damians_Fortress_1/Main/003_Static.dv2",
      "size": 3407872,
      "sha256": "e58e238ac23471543502b4ef70a89f3c3be51d2402c781a0ef74c4e2963f7fb1",
      "entries": 39
    },
    {
      "path": "World/Damians_Fortress_1/Main/004_StaticMeshes.dv2",
      "size": 1769472,
      "sha256": "41ff56533595500a9fe902c16c3994747ec2062933fccdf7f6fed59cab951344",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_1/Main/005_Streamable.dv2",
      "size": 5242880,
      "sha256": "618c459db9dc2a63e4ca43e3fb1ae206a230b2dc562d85d0e968f5cbcc37372e",
      "entries": 35
    },
    {
      "path": "World/Damians_Fortress_1/Main/006_StreamableInMemory.dv2",
      "size": 524288,
      "sha256": "1046eeb4b7568dec1809262bda4093dac8737a77058b64043c26c551d60210b4",
      "entries": 225
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Bonus_Dungeon/001_XMLs.dv2",
      "size": 32768,
      "sha256": "122ea444d2ec570790842ceac5a11b946842107f7802ba4a8cf80540eb464f45",
      "entries": 17
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Bonus_Dungeon/003_Static.dv2",
      "size": 688128,
      "sha256": "0ce377c41fd16c87504de639e08914fd8a19dc979d1525ed898c3a832bed972a",
      "entries": 11
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Bonus_Dungeon/004_StaticMeshes.dv2",
      "size": 294912,
      "sha256": "2367e2f06d0f2c69d2f239271d0331eae73c72be74f0b8e3f7e046764c2b07b8",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Bonus_Dungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "1bfe5968418fbad980f123c322ec29c36fa8981d2b2eb3a6995f9f1429bd146d",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Arena/001_XMLs.dv2",
      "size": 32768,
      "sha256": "0f2683ae307d4f45dcf5e6d0fffe34b7795a330d0498d6c8f3ba4b8d7d56d82f",
      "entries": 17
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Arena/003_Static.dv2",
      "size": 720896,
      "sha256": "407702ee7e950d6579a55a258a5328b95470c01f4fa730ad0fbbceaa3a752282",
      "entries": 15
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Arena/004_StaticMeshes.dv2",
      "size": 2686976,
      "sha256": "89efe5607c219f1853bb9632d5307911580898c0fe9a57987133124aafe473e1",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Arena/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "8dc972f652a0a63a2c02df47e535e5840dad6860a5238b2a9a7fb1f5bce2335d",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Dungeon/001_XMLs.dv2",
      "size": 32768,
      "sha256": "767fc3c1c269dc9325a2428089be6da428d01abe1adef99e22fdfc0d4a3d6f2a",
      "entries": 17
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Dungeon/003_Static.dv2",
      "size": 655360,
      "sha256": "1d93b2da3d251d8270fb047e932dba0f3f87641600cc6936c8248f929a575f39",
      "entries": 10
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Dungeon/004_StaticMeshes.dv2",
      "size": 2326528,
      "sha256": "b583c6303b031daecef549b0152de0107ac101773370681ca57dc40df729e587",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Stone_Dungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "8629b1570be951154207b9ebdc08cc0bf3a0680fcf69b63fad28c559bcbac97f",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Xanlosch_Passage/001_XMLs.dv2",
      "size": 32768,
      "sha256": "c3c352739bf387ec97745df65153921980108846e81d61fc969672cabcdd3a36",
      "entries": 17
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Xanlosch_Passage/003_Static.dv2",
      "size": 655360,
      "sha256": "4462e7ef3e5ca43639b148d7cf8f4ad4b264d73293d08be14f6e35c3baca12a9",
      "entries": 10
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Xanlosch_Passage/004_StaticMeshes.dv2",
      "size": 1343488,
      "sha256": "7d07a8e5b5c3ce540e67c6f4f6e9ecdef1610f80f6242ff2b4ca4f1d69d64ef9",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_1/Subregions/DF1_Xanlosch_Passage/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "45f178584a74135d37634dfbe83ff9f5219c5d690ac1bff9cee538d3eb82a4cb",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_2/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "dea1be355bf78ca8135136e996ef894ee267ba9ff0fc9be1c0c28b2dd01a5160",
      "entries": 18
    },
    {
      "path": "World/Damians_Fortress_2/Main/003_Static.dv2",
      "size": 3702784,
      "sha256": "2028422342ddab0539314236fb8d3abca3dfc327aa3e277b338b5de6c9cc1694",
      "entries": 42
    },
    {
      "path": "World/Damians_Fortress_2/Main/004_StaticMeshes.dv2",
      "size": 1703936,
      "sha256": "c2dfce2819beb962ac0b12eabd1ea9d6e03143e3111a934c8b5ac7edaf730ded",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_2/Main/005_Streamable.dv2",
      "size": 5079040,
      "sha256": "55a6c5164acdf8c491a36e8890670d984004656ede328836d1aaff40cb39b7b4",
      "entries": 34
    },
    {
      "path": "World/Damians_Fortress_2/Main/006_StreamableInMemory.dv2",
      "size": 557056,
      "sha256": "49c01d431eaf2b40e6027b736b16c3c6d6614bd50e67af2165c97122b419daf5",
      "entries": 241
    },
    {
      "path": "World/Damians_Fortress_2/Subregions/FF_Damian2/001_XMLs.dv2",
      "size": 32768,
      "sha256": "90f40a1238ac329edced94bc3e316aa993f5591cb13758196d53f4aff594dd99",
      "entries": 14
    },
    {
      "path": "World/Damians_Fortress_2/Subregions/FF_Damian2/003_Static.dv2",
      "size": 196608,
      "sha256": "63922818479506f46bcdbd9e4d80be24c780d49f2d5ffb15a0668c8b112ff73b",
      "entries": 10
    },
    {
      "path": "World/Damians_Fortress_2/Subregions/FF_Damian2/004_StaticMeshes.dv2",
      "size": 1507328,
      "sha256": "435a237b229414bba21b39e7b68f816a857a9bf3d71de2cca5d07196e4e19ba5",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_2/Subregions/FF_Damian2/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "35699e30efe0af0606b99ecb924321a10ded89d4fbf5386555df2481c97fe6b7",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_3/Main/001_XMLs.dv2",
      "size": 98304,
      "sha256": "c5646ab8de7573d80f2448dbc9e3a6fa7622aa857a9ffa78e4493f4539c210ad",
      "entries": 17
    },
    {
      "path": "World/Damians_Fortress_3/Main/003_Static.dv2",
      "size": 5472256,
      "sha256": "d62154db93937180716f78003b15a6f17c65c5e3bfbeb06081c332b9080eabe8",
      "entries": 57
    },
    {
      "path": "World/Damians_Fortress_3/Main/004_StaticMeshes.dv2",
      "size": 3670016,
      "sha256": "5ab58508e9df2bb6b94deae27d54958618ce1b3295b3cf08d852765bb4745aa3",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_3/Main/005_Streamable.dv2",
      "size": 7274496,
      "sha256": "f218b6839c728b29b0eb52450e887e19b923a58e5f798d7b859ebb3bd81da542",
      "entries": 56
    },
    {
      "path": "World/Damians_Fortress_3/Main/006_StreamableInMemory.dv2",
      "size": 491520,
      "sha256": "f691368675747aa0068292521772a6ae65dd45864aaf6257c67fc7841cd23bfc",
      "entries": 83
    },
    {
      "path": "World/Damians_Fortress_3/Subregions/FF_Damian3/001_XMLs.dv2",
      "size": 65536,
      "sha256": "959e2f20efda451df67684e6bcbc22f0fdcb5769db8798725b9c93d2f252b3e3",
      "entries": 12
    },
    {
      "path": "World/Damians_Fortress_3/Subregions/FF_Damian3/003_Static.dv2",
      "size": 786432,
      "sha256": "63fb853014144564af89d0cd12665dab5ee729fd63542a787e9cac40a6652e59",
      "entries": 11
    },
    {
      "path": "World/Damians_Fortress_3/Subregions/FF_Damian3/004_StaticMeshes.dv2",
      "size": 2981888,
      "sha256": "efbcb3ad6d71198ece57644958f9930910831f719ac7832b5faf1348be0ec202",
      "entries": 1
    },
    {
      "path": "World/Damians_Fortress_3/Subregions/FF_Damian3/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "429bdef99e9b0d3a3e7f1d091dc0ce560016f5b395baf0b56b7f2260e9b5066b",
      "entries": 12
    },
    {
      "path": "World/DZ1/Main/001_XMLs.dv2",
      "size": 229376,
      "sha256": "a86c9bb7e792db10b6dea294dd3c774ecc8eb4352221456f5638c099ddad91a6",
      "entries": 51
    },
    {
      "path": "World/DZ1/Main/003_Static.dv2",
      "size": 11206656,
      "sha256": "71a4096631f91811d96fec1db215c66fa9d10378ea397b3d77f6b5b267057747",
      "entries": 70
    },
    {
      "path": "World/DZ1/Main/004_StaticMeshes.dv2",
      "size": 9043968,
      "sha256": "b4a887ed85772750850869ca8de07447f801663c13f73a50f534ef3a3c0f3e8a",
      "entries": 1
    },
    {
      "path": "World/DZ1/Main/005_Streamable.dv2",
      "size": 24870912,
      "sha256": "fd0e0b95698783a66698ce7ed77624f18d1b9de7f52cb4605a8327d1a973ce83",
      "entries": 60
    },
    {
      "path": "World/DZ1/Main/006_StreamableInMemory.dv2",
      "size": 1769472,
      "sha256": "a1cfa69fed0b9d313573b059a94af2702b022c6e3bba58a903a2a6e9068e1670",
      "entries": 956
    },
    {
      "path": "World/DZ1/Subregions/DZ_Bandit_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "7c78577866fecb9679e0f3e5cc29e9331869a3d4e12b6ad8a63b30c0041731f7",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_Bandit_Cave/003_Static.dv2",
      "size": 524288,
      "sha256": "28af7200318a55204efb53f9bbf6e257e177b723372a6faca52233575825ff1b",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_Bandit_Cave/004_StaticMeshes.dv2",
      "size": 3801088,
      "sha256": "942143ada620af06f6f9b09abd1459603d644d409d80c78a30a659a1a4c468d8",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Bandit_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "40810b6d10cc9d2103b35fa725fa1c607c6c3edc0d70658f4778363994c1852a",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Creature_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "c6c60ea9ae52c30e13ed0a3c4282a00d507747f107d7693659854f0873cc7162",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_Creature_Cave/003_Static.dv2",
      "size": 458752,
      "sha256": "09d5a6f3610822e22cb5c4f948c32063195ed004914d7181a92f3ff799627b44",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_Creature_Cave/004_StaticMeshes.dv2",
      "size": 2752512,
      "sha256": "d48d75bbdc80019f49a3161c5ead6ac82d785827f5f2b4bd00ced9fe24f3b370",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Creature_Cave/006_StreamableInMemory.dv2",
      "size": 98304,
      "sha256": "9db4c63e5933837b1b2d5996030e664868787ebee1bbe69174146456e63e565c",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Depleted_Ore_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "531790a100576244b2f07499e390862d1a62ef5f394eae5be389af28fbc64f8b",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_Depleted_Ore_Cave/003_Static.dv2",
      "size": 786432,
      "sha256": "a3370a2b6f410571ccc5306136e84e5a1aa870e642193af78509539d62454d7a",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_Depleted_Ore_Cave/004_StaticMeshes.dv2",
      "size": 6422528,
      "sha256": "622bd265be625f5bb383731ffbbde797e8c598321af68265e651a44b752a99ea",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Depleted_Ore_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "17401bf680f275462c932cc97572f8d2c37425c4654728570c841bb6e157d2d8",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Halphas_Catacomb/001_XMLs.dv2",
      "size": 131072,
      "sha256": "54013711c9f473f4090c00339ad2c7f277d824acccea66e8932dbc00aabf01a6",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_Halphas_Catacomb/003_Static.dv2",
      "size": 294912,
      "sha256": "e5d004e1564e99c11fc2ad826e7fe5015e7f94c9e06be76563a9a301899a3f47",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_Halphas_Catacomb/004_StaticMeshes.dv2",
      "size": 1638400,
      "sha256": "1b504083323341ecd5d6a42c955804bc27c8e14044be6472f513ae8c1293901f",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Halphas_Catacomb/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "8e8d7ccf5c5618abd2547e291c5e8edb2613964198530986c17982c5a043d924",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Harbour/001_XMLs.dv2",
      "size": 131072,
      "sha256": "e6639693bb9c91be87bb17d8ccca5d22fd263d0296de9578324b6d3b3c15ec9d",
      "entries": 43
    },
    {
      "path": "World/DZ1/Subregions/DZ_Harbour/003_Static.dv2",
      "size": 819200,
      "sha256": "5cae07d2b6ce915be1c5a3f22231735461f735737d90dbf22966f5ba39c1a0a2",
      "entries": 10
    },
    {
      "path": "World/DZ1/Subregions/DZ_Harbour/004_StaticMeshes.dv2",
      "size": 1409024,
      "sha256": "93281947387c334b78982892e4a83873aca6a0884a52bf827dd78c79f135af85",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Harbour/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "ae2858fc29ed5cc5ffdb4045e41705a1770847ec643a40350e14ee1c17045eee",
      "entries": 12
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_A/001_XMLs.dv2",
      "size": 131072,
      "sha256": "6bb14124dc2ef1e49a820d4cd96baec7798c601883b045f9ef87c57b9fb1a9f3",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_A/003_Static.dv2",
      "size": 262144,
      "sha256": "cf0557cf9beb6f9e5df584edd62a5cf01aa5366fa5e382cfcc1fc1231d478031",
      "entries": 10
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_A/004_StaticMeshes.dv2",
      "size": 393216,
      "sha256": "a5c747b81e59ac10dd70017d2c534e33d86ee5995203ecc641f5acc992adf734",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_A/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "fc21859932984338679e182d67449303f829920c27f9bf867dd6cb49a8ea289a",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_B/001_XMLs.dv2",
      "size": 131072,
      "sha256": "cd62c9002048b7847ae9d0ac0cf256cac2840c6e5a36a062cb026e3cfdfca5f6",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_B/003_Static.dv2",
      "size": 98304,
      "sha256": "57158a0b037e4cb3a56722bf360d89b6110a44cf201e001cfca64c59c36998e6",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_B/004_StaticMeshes.dv2",
      "size": 294912,
      "sha256": "ad2806ca23f48697e54470b59d24dc36901c68b88d79becb62f12994e7b5c260",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_B/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "1319446d87f5273e23fa167e135acd6add441faac41fd2d931b1ec84dcf6d83a",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_C/001_XMLs.dv2",
      "size": 131072,
      "sha256": "7d7fe5fe95203191a859cde8e9971687ac195831d6fc7529f1b3875ae949b836",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_C/003_Static.dv2",
      "size": 98304,
      "sha256": "7702b249cffbc2f084f48cdcaf0af9dad5e8a1990e2b5fab795ef531050afd25",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_C/004_StaticMeshes.dv2",
      "size": 294912,
      "sha256": "b427b6e806c26e3f4b5ac7b31f926d554e241e9fccde7c623f6826b20d91a82b",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_C/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "2a4105fcb69e983ff1af4b395ba5f072a9d6dc248cdda8048dfb0617df6c7348",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_D/001_XMLs.dv2",
      "size": 131072,
      "sha256": "eb8585c42b7338f07e4c66e6fee813333379f682cc21ad2b4ec6c337ae3b9e77",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_D/003_Static.dv2",
      "size": 196608,
      "sha256": "7e5a14b2164739396761b57917a8073f0c1bb62c6cb3f40e4dc87001e805ddb4",
      "entries": 10
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_D/004_StaticMeshes.dv2",
      "size": 393216,
      "sha256": "929d043a7595aa6f56c0559f0bee889572adec139f1c0cf16fee86337033aed3",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_HighHall_D/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "a9a9722c11cd8b6b5ee2349291799ccb0c096e694a215205ce80403d6f606ce2",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Highhall_Demon_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "4f7e052e81eb674a4684aeeda3ca2bc89fad7fe180f25714509191f91e39502b",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_Highhall_Demon_Cave/003_Static.dv2",
      "size": 1310720,
      "sha256": "e5f3435b3036759a0685251b089a6844af11f1679b7137b19af2329c0f97832b",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Highhall_Demon_Cave/004_StaticMeshes.dv2",
      "size": 8749056,
      "sha256": "4a85e73a4738cc8b797772b0e0f85ed1c5916b2d7dbf02ec4b5415b921527d59",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Highhall_Demon_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "35f9bc7df3a518edee0e3315b78f923c56e526832787a6b4bf8e22c2b9740eae",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Imp_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "40af2d7582c0872a6d5cdc7a449bc9e802ab15c8c4bd9e786f5139e21ecf18e5",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_Imp_Cave/003_Static.dv2",
      "size": 262144,
      "sha256": "1de1db570e73296a15541b8db4dd27b53bcb65743a9c76fd4be56a20bbc7955f",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_Imp_Cave/004_StaticMeshes.dv2",
      "size": 1179648,
      "sha256": "89af5d624178c7e1df366b954c1fab2295393d9d12120a9b0deddc2e523188df",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Imp_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "0cd06c3656c8181d63b807d238a97a82bf09bdefc50ebdd045bc7a8b35815da5",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Mundus_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "351321c79beb9220e4251b820458f70385f19d887c6ee5ca888f67989bdbf4a6",
      "entries": 46
    },
    {
      "path": "World/DZ1/Subregions/DZ_Mundus_Cave/003_Static.dv2",
      "size": 851968,
      "sha256": "1955bae40bcf3be6102fa398423981f51b53394ed7777d7439fb5036fcdae02e",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Mundus_Cave/004_StaticMeshes.dv2",
      "size": 5996544,
      "sha256": "23476492f31b9f8fa00452870bd524fc2348e4f3978b5571f38dd5c1ba9ea31e",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Mundus_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "3cd903af481268fae14f5fcaf316429c2d22550fe840121543c3b52ce7f0cec5",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Necromancer_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "e35da9ecc0f46020ad910bdf171263deb1e91c14ef973c58f47ebe3c9811a0e7",
      "entries": 44
    },
    {
      "path": "World/DZ1/Subregions/DZ_Necromancer_Cave/003_Static.dv2",
      "size": 1540096,
      "sha256": "ebd64b3d5bf594d483c595773fc107bfde6116517033c32c2de299fd6b270f55",
      "entries": 4
    },
    {
      "path": "World/DZ1/Subregions/DZ_Necromancer_Cave/004_StaticMeshes.dv2",
      "size": 10027008,
      "sha256": "eaaa1b5cb70a6a40a11619ed54375cd57674cd9adbd38f39431112ebfed938cb",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Necromancer_Cave/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "693349b260e4c45193ff10117cde8bd23b232f6c578168dc910464ba25c29abb",
      "entries": 5
    },
    {
      "path": "World/DZ1/Subregions/DZ_Patriarch_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "f5eedd14f7b08589133537489e8f4893a6d50d4780dcccc2cf8777ff8f3dbb9b",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_Patriarch_Cave/003_Static.dv2",
      "size": 1343488,
      "sha256": "d515d5ff2caf8dbc87a55130a05d49748b251c29df2869eed66f72e3cee9cadf",
      "entries": 10
    },
    {
      "path": "World/DZ1/Subregions/DZ_Patriarch_Cave/004_StaticMeshes.dv2",
      "size": 11010048,
      "sha256": "5bc301c8b10e95bd527ec313b81c4de98ed9dbb37d97ad45d4a6840312655a43",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Patriarch_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "6ed7eeb57ec788e61b1cea86cb2b964c0a1c479704a6f3b8d6bd7594c404359b",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Svadilfari_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "ed96fda8b81e198e5539f5755a1a2f130afc9c851ec432d399921d352355e024",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_Svadilfari_Cave/003_Static.dv2",
      "size": 753664,
      "sha256": "a6abf730cf2ebe5e212d1dd741c2637d3d2d0ebee4b2c2829612e1063869d2d0",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_Svadilfari_Cave/004_StaticMeshes.dv2",
      "size": 3014656,
      "sha256": "796ee6b40e7eac03c2f26376cbae69e3d7e5edd4711f5e606e90b90f0ee53bbb",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_Svadilfari_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "0ae270106663fdd11b25c7eab80ac1bd7903dc7866ed82be3544f175565fccbf",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_The_Morals_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "08199ecc1c08ac4a33c9844642fd33f8c48a326537a7dbbd3d7095cc625f0cfd",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_The_Morals_Cave/003_Static.dv2",
      "size": 819200,
      "sha256": "ee7b05afb8651d73bdf46a2c5326ea0b55b3b5d160640a05e49a9a6c4ccf5a1f",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_The_Morals_Cave/004_StaticMeshes.dv2",
      "size": 3342336,
      "sha256": "fd05a82b4f5d30f3316a86af088c260273757840b5add0a08b33520569f28e33",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_The_Morals_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "5db5b56b453d9c3e3952f80be4712fe5664e91c392e67470feaf5aef056bd0de",
      "entries": 11
    },
    {
      "path": "World/DZ1/Subregions/DZ_TombRaider_Cave/001_XMLs.dv2",
      "size": 131072,
      "sha256": "a055547482646d0e51be5d888711d9eb49e68f21df0ae42760b80a43296a9950",
      "entries": 45
    },
    {
      "path": "World/DZ1/Subregions/DZ_TombRaider_Cave/003_Static.dv2",
      "size": 262144,
      "sha256": "15e68429d6d0ee12ee56b44d642be886a4b7c3b38318cae018a698cb5a1bfe4a",
      "entries": 9
    },
    {
      "path": "World/DZ1/Subregions/DZ_TombRaider_Cave/004_StaticMeshes.dv2",
      "size": 1376256,
      "sha256": "f90b42802caf16c47df3979a0ebbe2a938c10cc1808f2a0169eb28371b9e1bbd",
      "entries": 1
    },
    {
      "path": "World/DZ1/Subregions/DZ_TombRaider_Cave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "97562f161b52801d6e33544f37fed44b0f770df22519294c8dc63d3daf2c6a52",
      "entries": 11
    },
    {
      "path": "World/Exp_AlerothCity/Main/001_XMLs.dv2",
      "size": 229376,
      "sha256": "e9669a6c1ebf4dd8442e74f8630169fb8efe91ec49a7c5eca819b1be54c222db",
      "entries": 70
    },
    {
      "path": "World/Exp_AlerothCity/Main/003_Static.dv2",
      "size": 5013504,
      "sha256": "a9bbe42d03784ae5c1cf150c4f9a4eb10850dd09840d3f603a3152624d6fe73f",
      "entries": 101
    },
    {
      "path": "World/Exp_AlerothCity/Main/004_StaticMeshes.dv2",
      "size": 40239104,
      "sha256": "6decdb89aeb4b7486c144a0ac5534709e237393fcd8f571c3c825fc57a64c9eb",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Main/005_Streamable.dv2",
      "size": 2457600,
      "sha256": "683a2608e123d72191d7d5fccc1c2852fee2d169ca1eb2fea8fda1cc6c399a3e",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Main/006_StreamableInMemory.dv2",
      "size": 1605632,
      "sha256": "26c7178d8f5e3c7cfd685c184648b46461c6588512897b96e5e38c2cf52e2640",
      "entries": 185
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCatacomb/001_XMLs.dv2",
      "size": 196608,
      "sha256": "dbd81e5af87a4bf4c59e85bc7cb850ac0ae980558aad0b004be1d7152ac4962e",
      "entries": 65
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCatacomb/003_Static.dv2",
      "size": 557056,
      "sha256": "5e2f36f7b08a18e1818131e35218230de5425e7c279da11e98f7440ace4c8f4a",
      "entries": 10
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCatacomb/004_StaticMeshes.dv2",
      "size": 4063232,
      "sha256": "42795a17e310b281e5e42c9d22dd8ecb5e83a41148000c7e93b4178b02135885",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCatacomb/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "bebe939e59e4c2c647ae5a3f15604861243728ecdc40bde6c5d2099ad9756be6",
      "entries": 12
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCave/001_XMLs.dv2",
      "size": 229376,
      "sha256": "d1480edad8162422f1892c56f2cd4ed9b77d207866479bdf03a57e934358631b",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCave/003_Static.dv2",
      "size": 884736,
      "sha256": "315a16d4f9ff89babeddf1e56f81ace5585cf0f8dd54d83d2346d4620cd964cf",
      "entries": 10
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCave/004_StaticMeshes.dv2",
      "size": 7208960,
      "sha256": "8429c33650dba7ec7e781950f75eac0172ef0e12fea5849aab63db0d025f71e2",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AbandonedCave/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "481adc6bc8ccd6fd7016782781958954b73233d404fdae92db9b80bfb80f1b97",
      "entries": 11
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlerothHealersHouse/001_XMLs.dv2",
      "size": 196608,
      "sha256": "67d9464a5c5f790fbdcb660b09fe7ad30960069f213457f7a7ffaa95f72ca9e5",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlerothHealersHouse/003_Static.dv2",
      "size": 720896,
      "sha256": "67f891272fd4ea22ee19781dacef4a8948c82cf5a401df68d728505675f05bbb",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlerothHealersHouse/004_StaticMeshes.dv2",
      "size": 1343488,
      "sha256": "bb8d88c64a4b213bdea2f9f7bc85ec49968a7aef4a1ce8b1cd665029b30c8f03",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlerothHealersHouse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "9dd31b39b19aaf10ee149e158909096ce1daee82e49393886eac0ce173c4fb01",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaDungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "6f406d5b791dc2f754ffee413106562c026f4b75e9d0b46330b515f0d4643959",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaDungeon/003_Static.dv2",
      "size": 196608,
      "sha256": "8b16a7b7c3df63c750fd38ef71afefac005b75ff4d0cba156fa53bee6f862f62",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaDungeon/004_StaticMeshes.dv2",
      "size": 720896,
      "sha256": "a940b6aa8186a9a1ee6e28009c16d38926a6b892bc8e3e611e4af9854a16720c",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaDungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "c69d615e4eee3529ee508cbb05386b5a49c0bccad8ae7977a586480b84cc563b",
      "entries": 10
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaHouse/001_XMLs.dv2",
      "size": 196608,
      "sha256": "d38544fb8820b56b1e62c3dc21f630ea79d9332f3b70ed7620d18d14d672d7cb",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaHouse/003_Static.dv2",
      "size": 262144,
      "sha256": "4592b1bf826e5d5acb71daf67da54c6706a6e428425b26629d7346b5b558aeee",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaHouse/004_StaticMeshes.dv2",
      "size": 524288,
      "sha256": "9ee7024f845d0223e873f68f92c9f1e704901c897479764f27fbd77164ef4ad3",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_AlzbetaHouse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "e80fa9060cda74eb40e78ccb605bb9378d14d72a285f095fa01ebc790fdf9f78",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_BlackMarket/001_XMLs.dv2",
      "size": 196608,
      "sha256": "e0bea37115769888c62dd9d456fa636e938886b48e680dcb2d4459cbff8d95c3",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_BlackMarket/003_Static.dv2",
      "size": 360448,
      "sha256": "e3d4855d841122526ff75edb943e14ae01e957681e1f36ee9f45d08f44d95162",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_BlackMarket/004_StaticMeshes.dv2",
      "size": 1048576,
      "sha256": "30125d73fc214b8a7b4e6da0a386285885b511d9b979b1b7561bafdfe52e0407",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_BlackMarket/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "497077adf841111997d7cd8ee9830603d4f39f95edd1866458eaa8972ba2d295",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionAcademy/001_XMLs.dv2",
      "size": 229376,
      "sha256": "dfe7b769c5babe8d964c8c4904bf738fd7e2bfef427ef047f76c2971991644f9",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionAcademy/003_Static.dv2",
      "size": 983040,
      "sha256": "378a75cd530218787cca17279b73af50c39c342339d3332d854920df39f5b571",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionAcademy/004_StaticMeshes.dv2",
      "size": 11075584,
      "sha256": "f26b19aa25a8894830cfc180cc2ac9d0f2a3265acc3608b28887b4b2a2bcc005",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionAcademy/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "ad0dea4ed7bbca17c6ec97af5057a540d9b1733040282d5313726e7bcbce7975",
      "entries": 12
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionDungeon/001_XMLs.dv2",
      "size": 229376,
      "sha256": "aa44203c8d26c24990a8a1832ad39b690466a79d44142b7cb09f1b6502a7fafb",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionDungeon/003_Static.dv2",
      "size": 655360,
      "sha256": "24b8acc58f43ca0ae35e643808027a6162e7a81f65325819b3daea82ab92ed93",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionDungeon/004_StaticMeshes.dv2",
      "size": 5439488,
      "sha256": "637d06a3f8215473497e71f8da7d9d170ef0641fbada230367850b04ea2edcf3",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ChampionDungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "a5ef369cbafc6d641ab26cadbe766a1a934c4d49efc2ee7a7bae849262954153",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EmergencyBarracks/001_XMLs.dv2",
      "size": 196608,
      "sha256": "f93bc2f5ab8818f5ec90db10a948a3e3aeae371c9d195e93f65da312bdb177af",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EmergencyBarracks/003_Static.dv2",
      "size": 1015808,
      "sha256": "1ab4285b9a6d81f5e4b2c66ee3100a623547ad48bc1990f1117d1d5b70341fce",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EmergencyBarracks/004_StaticMeshes.dv2",
      "size": 1343488,
      "sha256": "9c6147cae2115c21d67d592a7b507f7a694dc3c7805a85d33fe0f25bbc2edead",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EmergencyBarracks/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "6cab49a4950a7ea2cce288b62e5ac8c048edf70bf4c701a55fe0257c8da1f7a7",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EngineerDungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "72bc503a62c8a2e98f5b8589c43f62a74e4a2faa3cb6306fd5cf35fd36f0e077",
      "entries": 65
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EngineerDungeon/003_Static.dv2",
      "size": 131072,
      "sha256": "f3a6f25a94547dbab4464dc73cd9a92bed6d80b55dfbafaffe1466ef83c8be8a",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EngineerDungeon/004_StaticMeshes.dv2",
      "size": 1081344,
      "sha256": "95c5ecda8b374e3e36e0c5cfbaaf47b64a18441c01538f020308a86d2ecd60ce",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_EngineerDungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "031476fa91e187c06fab97a202ea7ffa619c4b0ea7e857c4f30ccdc6c0cd4ecd",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01/001_XMLs.dv2",
      "size": 229376,
      "sha256": "7e6138492b2f8cd189b3f905bbbbfea0c00c1e86e963a301bf0908aa39a9470a",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01/003_Static.dv2",
      "size": 163840,
      "sha256": "d805f8c8635a1af0aa377e3f6800b558702998958e33a8fe29901dd0f486d26d",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01/004_StaticMeshes.dv2",
      "size": 2555904,
      "sha256": "41be10d064e5b25a0d232b9e0865ecc87a7d8d3c9bcbd10812cf4b485bdc6c3b",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "f7c84250186655e87d945ad41d73576aa62bfb18c5c80af03d53088313a08140",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01_Dungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "12e3928041e6946d7516fd0924275d33bf3f1b2ff19a0e64d7f030b433646c8c",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01_Dungeon/003_Static.dv2",
      "size": 98304,
      "sha256": "ea334ff01de94f32ad0257733fd14f2ea1a169482173a56b9a5090b6036c1370",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01_Dungeon/004_StaticMeshes.dv2",
      "size": 950272,
      "sha256": "53c2111fd343eacfa15a8bfb35a86a91972a4f56876309ba2ef2feb15389384e",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_01_Dungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "ef2fe5cf151ed9806304026a20462e185620a8a3babab35232601883c32a9e81",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_02/001_XMLs.dv2",
      "size": 196608,
      "sha256": "46c1ccb9bbfa0ae5b5e8965c3f4b5d1834359442a492847b17dca4ef314e0ed0",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_02/003_Static.dv2",
      "size": 229376,
      "sha256": "4c5d56f9b71c98fafc5c07ef59d4ec0d00afb112aec849f53f44c9e83ff71e49",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_02/004_StaticMeshes.dv2",
      "size": 1671168,
      "sha256": "a42eda626911bf9804d9a56b61753e23b9a806323d00f1570213c88bc9b4cad8",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_02/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "f461d2d13680b8ac17953ff10de5eb8c155b07ff6b4061578f11d0bb8043522d",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03/001_XMLs.dv2",
      "size": 229376,
      "sha256": "82b9e92444e2c75220374d3a8471ae65a6851610f43e20227c6c60acc4a5e1ef",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03/003_Static.dv2",
      "size": 229376,
      "sha256": "5c8e24ef84c29d209f8ff5e3e5b462878f957680cdcd6c01deda42edaff90d18",
      "entries": 5
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03/004_StaticMeshes.dv2",
      "size": 1933312,
      "sha256": "0babe506df3f5acf54c93739c531715d5b58b0edab53994a337cbfbcd145c16f",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "6e2a7a9439a854ef98e9016519e96e6fc682b6ab3ac037a4dd6a9aff2da81706",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03_Dungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "29a21eb39f02e29b95da71f0e73ee88ede336e70febc68c1790b7f7f24366213",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03_Dungeon/003_Static.dv2",
      "size": 163840,
      "sha256": "081eff1e2bb5dcc700320c4152945545124ca9866746cba75cd61b7f062dc70f",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03_Dungeon/004_StaticMeshes.dv2",
      "size": 983040,
      "sha256": "2436fbc2d2dd672abcc7bbaf5a384408da6d1b96617f4c165ba62c6caa0cec82",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_03_Dungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "5277bb26922f2a285cd657b15e707d14a415ed35e321d2eaf3d396f1f7493056",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_04/001_XMLs.dv2",
      "size": 196608,
      "sha256": "2d8118ca97c34362ea832ecdd9133d97fc1af0ace527f51623acb1adb2b022be",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_04/003_Static.dv2",
      "size": 655360,
      "sha256": "40f06ee19c46c93651b70ae6b4cfd9ff74bf6023a065d39064b8c57fd1492529",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_04/004_StaticMeshes.dv2",
      "size": 1671168,
      "sha256": "0f0a5d0540ba7d5267e7ba8a083fc75575756e21dc40be81f26d9fa27604a2b0",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_04/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "df42bfcb10fa475515078180c2ec7a48e8b2c9e54c48e9d8869ac19c18c33e6e",
      "entries": 6
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_05/001_XMLs.dv2",
      "size": 229376,
      "sha256": "48e945e3aefb68092da88a88cc3b8d4f2fb4325545e7180b4ce7a16380bed936",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_05/003_Static.dv2",
      "size": 229376,
      "sha256": "7e5eb42d6358dc5905c4af79e59a5043a8fa2c692bd879901bc703adef3a3d00",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_05/004_StaticMeshes.dv2",
      "size": 2555904,
      "sha256": "d638bbcced3ec0ec36df81fb5491cc42e66834a6abb067ceb3274334b30d681a",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_05/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "cb1628cf5d75bc9dcffe0f702fa489af43807f5ff6ea2eb0923838d1bcfcdf58",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_06/001_XMLs.dv2",
      "size": 229376,
      "sha256": "bcdb45b69a051ce398f0e7bc2f6fd042777a58ac4e3a8d48e0f10995a59e4579",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_06/003_Static.dv2",
      "size": 393216,
      "sha256": "802e9ddd98534b622bad79a5d598e144728729baf456ac375feda1a78ead895d",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_06/004_StaticMeshes.dv2",
      "size": 1769472,
      "sha256": "3abd1a2f9903348b63f299175df36894afe6cef3978e87da825f0bf574c7bf1e",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_06/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "2bab212a94072cdba17a66c936e28a35ef30b2d80df63c24fd82cb1fd90c5df8",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_07/001_XMLs.dv2",
      "size": 196608,
      "sha256": "c28ea2f4dc09765e41a689e5804de52b8d68873f762d711e36a28f2d9bb63286",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_07/003_Static.dv2",
      "size": 163840,
      "sha256": "57c17020bc8d15a8731cde4ef8996258e717e776e8fc4a2ab46971328e0e23d1",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_07/004_StaticMeshes.dv2",
      "size": 1179648,
      "sha256": "47fd3b7865631bb1db45dd960973d1d850afb614de5fc0ceea1d92a297b995bb",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_07/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "6cd611f4551c2f70682c5305974559c1977058a10828eae6409c69c285e5a16b",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_08/001_XMLs.dv2",
      "size": 229376,
      "sha256": "841199730f49c0ad62eb60e6fcda4cb75c27b2e84776de9bb6378be42366b868",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_08/003_Static.dv2",
      "size": 196608,
      "sha256": "7a2c978f13cd3b533cc46c0984e38e22f876b2ae7d4b8384f1ee8eccca91f38a",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_08/004_StaticMeshes.dv2",
      "size": 1769472,
      "sha256": "55b55e47bb52896783db31d9b27ad28b3d8ec646b4fb2988a4995a3e42196259",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_08/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "1d9d6211676d70d9b3e6ecbf53086c9ad28a59de179832f9d7990017145ad5bc",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_09/001_XMLs.dv2",
      "size": 196608,
      "sha256": "20bb3bdb7a6682ff01cd023ee4510839eb8ecf4dfed1b3b57f7fce6e7c31cc81",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_09/003_Static.dv2",
      "size": 163840,
      "sha256": "769e9123a9b36e43eb87595c4e35ed2098c46b5940adcc7a55926c75b5e693f7",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_09/004_StaticMeshes.dv2",
      "size": 1703936,
      "sha256": "ce4e9814b89e9b22b5f543c50d73323464c2d22b4fa381907f74137944a69aab",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_FightHouse_09/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "15724a20f9bdcb54eed7296b735f60c66ced01ea4505b356e6a6109a996b942e",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_GulaHouse/001_XMLs.dv2",
      "size": 196608,
      "sha256": "7408dcda42c4a87c8fd62ee06b06105732826b12494dba610774322c0ca9bcda",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_GulaHouse/003_Static.dv2",
      "size": 229376,
      "sha256": "1814d528cc28396d930dd1b52b380a57b01192dcf78295a8bd661df46f0b5451",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_GulaHouse/004_StaticMeshes.dv2",
      "size": 1736704,
      "sha256": "082f1a008166b01209770b258f3214d8032e0555c7f2c55ccbec7258de9847b6",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_GulaHouse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "77fa0cdca946d3ba42c8c54be90d3dde8ed491107a7ec21379dd52c3d1d67680",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HaremBackdoor/001_XMLs.dv2",
      "size": 196608,
      "sha256": "ddd848226a989434ac7692c5566199b3eca5a3748bfec26b366a967f58813da2",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HaremBackdoor/003_Static.dv2",
      "size": 131072,
      "sha256": "439e1b75103d74719f36a36fad5a02859d2d429dae34dccb4d99b26c7d05cc71",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HaremBackdoor/004_StaticMeshes.dv2",
      "size": 1540096,
      "sha256": "5300fdc5acf67fec32f923c5d4f3f6b835424efa94c47f52510cd2d956523f2d",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HaremBackdoor/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "bc364748e909d00ff233d0e65f837ff1ec639f6a3a6127c6d05e539fe3834a0d",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HeleonDungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "47e16aa377844398c71bf9173ec69e029035258d90219bac9a73fe23f6f71ba0",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HeleonDungeon/003_Static.dv2",
      "size": 360448,
      "sha256": "71b63650dcd1305649b78988ea9a3162810371681d33a262a3442ed9e3ba6346",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HeleonDungeon/004_StaticMeshes.dv2",
      "size": 2064384,
      "sha256": "84df21414d6f6f5e10b99852c8f5c9f7fd933fa455c7f80aa40478f0ad691c6e",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HeleonDungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "e2c42975c23a35160ac8b60536f5b3df69e772bd3285043ce653af9ec34994bc",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HellishDimension/001_XMLs.dv2",
      "size": 196608,
      "sha256": "6eee258d0298c0a7956204cccb747978d3b0d730e102bce387488c73f96fa1d0",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HellishDimension/003_Static.dv2",
      "size": 720896,
      "sha256": "1273e60384da4bdde2f0e33264548e7257c1b0ce9517a816de5730c4e5a934da",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HellishDimension/004_StaticMeshes.dv2",
      "size": 4259840,
      "sha256": "d7736acdb7a126842c8b7fca881ee62b6b1779aa8aefc5cb43f4e61e307bc33f",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_HellishDimension/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "f5467c6264d3e82cb1e0ed4521a4d411c2c62a06c4f3242f5b5bb5d1f289385f",
      "entries": 5
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LeverDungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "a2116142b9a1bf2ac48ff61adb28b823f0ccded2ac3d1bbe04a21cafd5c2bab5",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LeverDungeon/003_Static.dv2",
      "size": 196608,
      "sha256": "d8765dcb57c014fdcb0b8b5b7c34c6fad2b59bdb309d2a9b6778bbb37a962c1f",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LeverDungeon/004_StaticMeshes.dv2",
      "size": 1998848,
      "sha256": "c8263c6fcbcfcda4c6d023199a2380971460b19ea0a9645631595e7b7d707f15",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LeverDungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "4de5d74e2d47a60be9293c4396154ae64a6528793e1f86369ffd19cf8aac1d88",
      "entries": 14
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusChamber/001_XMLs.dv2",
      "size": 196608,
      "sha256": "45f4fa464d28020427a0ea02cff41ed5323a16b5149087362d95f808637a50b9",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusChamber/003_Static.dv2",
      "size": 557056,
      "sha256": "34986e8f475a0cc85862ef798d8f0471b79ca148f6fdc45df9d13a1047e08bb9",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusChamber/004_StaticMeshes.dv2",
      "size": 1179648,
      "sha256": "3c55c53c3c9703b0269f8861e61799e1908e209882dc9a713273caa5ffbf8c62",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusChamber/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "da18e44711a46681b0413351d5fe7447d751bc7f103d5275b4c58f5bb84e910e",
      "entries": 6
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusDungeon/001_XMLs.dv2",
      "size": 196608,
      "sha256": "9e27f05f9751d25e92750e402d7cebd4fa08884c25a67cd3b89428a1824f63d6",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusDungeon/003_Static.dv2",
      "size": 229376,
      "sha256": "e40e6806a626434f15fc33b5b2de17753b472d329b39c80378e2332bba3cc021",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusDungeon/004_StaticMeshes.dv2",
      "size": 2523136,
      "sha256": "57f5922d1c0bfe2f00964afc7f9c474842610e8f0f129e92784f160a048f9866",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusDungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "bce15cd09bb700ce63e81e6ee8a5ff15433cda7393123542d6954e4455a8a36c",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusHouse/001_XMLs.dv2",
      "size": 196608,
      "sha256": "0d3009c4d05c718532ba8d8fb463ecaf4d616104b3434d969d1a32e52b0f1fc8",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusHouse/003_Static.dv2",
      "size": 196608,
      "sha256": "b34f304fec573f0531ce080781d1d5764d1d8267edef4114e5898c45aa6343da",
      "entries": 10
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusHouse/004_StaticMeshes.dv2",
      "size": 1736704,
      "sha256": "0982ade5ed4ee02fd8c8c9984a27fdc127f2572341f1be497b9bca95db245814",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_LuxuriusHouse/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "e61ffbb2b9f421b58e2780207b7186829ecd64cf8ab72e37f854c454ab3500ed",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_MadamEve/001_XMLs.dv2",
      "size": 229376,
      "sha256": "85e3213798e5a0b75c2952956a5d5bcc61edc025cecefca84d2e6db0907041a5",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_MadamEve/003_Static.dv2",
      "size": 327680,
      "sha256": "f8d0c6748309a48034197c9bce77a4098eee88fa642e729bf8e0e16514e94f89",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_MadamEve/004_StaticMeshes.dv2",
      "size": 1769472,
      "sha256": "b2d474daac345a85af71e3b007eaf3a4d5f0369275b049b8f2a31bef0b6a32ca",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_MadamEve/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "c32d992cd480f1edc1514a3e058ca110d443447672a23ab2b54c7b2e58c678e3",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_PerfumerHouse/001_XMLs.dv2",
      "size": 229376,
      "sha256": "2e49ebef0cd9c67b95c7a5edb0975a55a30eb05dbb91267551d01dd38c64188f",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_PerfumerHouse/003_Static.dv2",
      "size": 163840,
      "sha256": "9d85e558b91c840e16f9e217f5b32222f7def6a0cc56ac507b5873ceae5d81f3",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_PerfumerHouse/004_StaticMeshes.dv2",
      "size": 1736704,
      "sha256": "41c1a64a0f910f8bb32e189ee1758f0180f9c48d44dace82617e8f97460e09f1",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_PerfumerHouse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "7e6d53c7d5c52d472fc636271573383d837119f236e6e9c21e51f2f5a71def48",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePhoenixInn/001_XMLs.dv2",
      "size": 229376,
      "sha256": "cdc81323c7cde357cb87ee0c8bfd19d17f8439be962db19c9d240e259389d828",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePhoenixInn/003_Static.dv2",
      "size": 1212416,
      "sha256": "2d17ba1cb300b2ba5567d0f667ae33e940fe230f7bdc6e0f7a183000a81ad372",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePhoenixInn/004_StaticMeshes.dv2",
      "size": 2719744,
      "sha256": "5989b6e7caadcdae11454da34672bdc7be801fd8248c8607690fcec55b1ec1c5",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePhoenixInn/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "572fa1deab9993613595a3dbe5f40be6748d430321834a45715e8a249eba7d33",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePrancingSeahorse/001_XMLs.dv2",
      "size": 229376,
      "sha256": "4d614a363408b1e71c58bdec07ddac506eb5f5763b02aebfeb2ccc7534348988",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePrancingSeahorse/003_Static.dv2",
      "size": 786432,
      "sha256": "20f9a04764249175623acaf7495cc27597163c81d813cbaf4ec8296a29557787",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePrancingSeahorse/004_StaticMeshes.dv2",
      "size": 2392064,
      "sha256": "6cffd04bb53519adec59bd0d837179722b60f1b87d2c893ca736b936d7e9cdc9",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ThePrancingSeahorse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "194e9b14a3defad1e1599ab6e7ae5960082fdf2cc06ada7afcdc668b02dc7960",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_TomsHouse/001_XMLs.dv2",
      "size": 196608,
      "sha256": "e8cc1916ad4cf5dab3c52669239bc55154f3b991b1564629734328af48928c87",
      "entries": 64
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_TomsHouse/003_Static.dv2",
      "size": 360448,
      "sha256": "47d2d13f4d2864c557dcd6eb0e485c9e7dc60e02f4a7774f358f3d071451ef60",
      "entries": 4
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_TomsHouse/004_StaticMeshes.dv2",
      "size": 1540096,
      "sha256": "3b903da91da226b62ae70f6a990152893125c4e0048a9810c25fb3142d9630fa",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_TomsHouse/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "5ff3c53200da201160aee119e47c1d2d8547dc774ee039e1ee3adfae19eeec0e",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_Waitingroom/001_XMLs.dv2",
      "size": 196608,
      "sha256": "979ba58b8878c336899cf3fde90fb330e751fe33ea891a256dcf00774f0090f9",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_Waitingroom/003_Static.dv2",
      "size": 1605632,
      "sha256": "2a5eb3b6f049110b16da362246e99c90292392388bcce9adb01bff68a0cf595a",
      "entries": 10
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_Waitingroom/004_StaticMeshes.dv2",
      "size": 7307264,
      "sha256": "ea8ddd2483f0aefe24d0ddaf082851f6115b4ee2fe14f70428cf872ad370f67f",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_Waitingroom/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "31b1fadfbf416cd30e1e7619987cb2ecd1a3e144c58cbf77db0134fb88c6eb6c",
      "entries": 21
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_WispDungeon/001_XMLs.dv2",
      "size": 229376,
      "sha256": "562fcc733281ab477a8c614013c627c3677ce6c97a8c1ec4d3b9bb2676c8438f",
      "entries": 63
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_WispDungeon/003_Static.dv2",
      "size": 983040,
      "sha256": "4ec347ca56d9d6df2d9af786a7e2301668ef36168512196d7d3d890522cb7c9d",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_WispDungeon/004_StaticMeshes.dv2",
      "size": 5472256,
      "sha256": "bdc2e8f1a1fa63096e94690fc1050c22059e3b7e66bd20124019fec6f109556b",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_WispDungeon/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "000e6634414c58d7d67b43fb90d167c6b17f9c49076ec7cb57995f1a105b56aa",
      "entries": 3
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ZombieJakeDungeon/001_XMLs.dv2",
      "size": 229376,
      "sha256": "a2988a7941f0e38d11e7e41a91cf02b9006b35e79cf668bff68695bd82ec55d3",
      "entries": 62
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ZombieJakeDungeon/003_Static.dv2",
      "size": 425984,
      "sha256": "96353ea30c49a1db7b1d478a217a10c8e273c9ff78228abc33d053aff5af9b9a",
      "entries": 9
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ZombieJakeDungeon/004_StaticMeshes.dv2",
      "size": 3014656,
      "sha256": "124eba071efa815ec37c36686ca601de54f12ff0f434220de30a2d2fcebf520d",
      "entries": 1
    },
    {
      "path": "World/Exp_AlerothCity/Subregions/Exp_AC_ZombieJakeDungeon/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "2cf08647fdbc5545c365198000499bff2076cebc2295e140731b4b547545cffb",
      "entries": 10
    },
    {
      "path": "World/Exp_AstralPlane/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "45bcd39832b5f29312477407b219a7089a8ee300ca777d4bc9677f17c4f28a05",
      "entries": 12
    },
    {
      "path": "World/Exp_AstralPlane/Main/003_Static.dv2",
      "size": 884736,
      "sha256": "7830aa746a4ad5572807aebf85c2861c58c7e507eb212694cb9229237804a8f5",
      "entries": 30
    },
    {
      "path": "World/Exp_AstralPlane/Main/004_StaticMeshes.dv2",
      "size": 5537792,
      "sha256": "caeb0299caf46c4940d01b2d4902b466aef28c6313432848ca29791652f8e2f7",
      "entries": 1
    },
    {
      "path": "World/Exp_AstralPlane/Main/005_Streamable.dv2",
      "size": 3178496,
      "sha256": "7deb1f7feef1139c4589eaf7f12f657329bb4558a46be039d6346cfc9ebda685",
      "entries": 16
    },
    {
      "path": "World/Exp_AstralPlane/Main/006_StreamableInMemory.dv2",
      "size": 98304,
      "sha256": "9bf6874b7f7dad82c2a8de8d49aa53597920e1da81061321bb1c1f3fa5023009",
      "entries": 35
    },
    {
      "path": "World/Exp_DamianFortress/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "51b2d5088c10882c41c46ba8f5002fae4a4134d103ce411f7d18af96bea36867",
      "entries": 14
    },
    {
      "path": "World/Exp_DamianFortress/Main/003_Static.dv2",
      "size": 1474560,
      "sha256": "5eb15fd92397629a81a7ee80b1137e7fb10d74f49de099bba1b53215c0651201",
      "entries": 10
    },
    {
      "path": "World/Exp_DamianFortress/Main/004_StaticMeshes.dv2",
      "size": 32768,
      "sha256": "96f387c296878c303d4ab99d89a298675a85fa17e4d825ce1132f9ac053e355b",
      "entries": 1
    },
    {
      "path": "World/Exp_DamianFortress/Main/006_StreamableInMemory.dv2",
      "size": 32768,
      "sha256": "ca312a91bf9d7fb9e3377135f33848410971648760010ebcc35a61514969d605",
      "entries": 6
    },
    {
      "path": "World/HoE_DreamScene/Main/001_XMLs.dv2",
      "size": 32768,
      "sha256": "522ba7072934167cda9e19308372c5243c78b7fa4424fa6b19fc61b086548337",
      "entries": 16
    },
    {
      "path": "World/HoE_DreamScene/Main/003_Static.dv2",
      "size": 12386304,
      "sha256": "381779d9388d009c6b0b67e033592e64758231418d556a0c74b3e41e5d67d90d",
      "entries": 46
    },
    {
      "path": "World/HoE_DreamScene/Main/004_StaticMeshes.dv2",
      "size": 2097152,
      "sha256": "c51e6439dc50b6e6a5011146822b6e123b71a73684c5345925bb5e33d4a6277e",
      "entries": 1
    },
    {
      "path": "World/HoE_DreamScene/Main/005_Streamable.dv2",
      "size": 4915200,
      "sha256": "699292137ac37d1ebf8a509e13e8011664fa30f868ef6f859bea737b24de128b",
      "entries": 51
    },
    {
      "path": "World/HoE_DreamScene/Main/006_StreamableInMemory.dv2",
      "size": 327680,
      "sha256": "ed3a3db06aebe96d62adb6703eac3cfc201d1f4d5983cf26d53edb7721db2807",
      "entries": 36
    },
    {
      "path": "World/HoE_DreamScene/Subregions/Hoe_Execution/001_XMLs.dv2",
      "size": 32768,
      "sha256": "eb89d21872bc674e5a82173a2d1111a047baf460d68817a26f437a8aaa71beea",
      "entries": 12
    },
    {
      "path": "World/HoE_DreamScene/Subregions/Hoe_Execution/003_Static.dv2",
      "size": 163840,
      "sha256": "503ccf4567bfa9b9fe359bb93e2ff4953843e1116b0d42bbb9013702d1e191af",
      "entries": 10
    },
    {
      "path": "World/HoE_DreamScene/Subregions/Hoe_Execution/004_StaticMeshes.dv2",
      "size": 753664,
      "sha256": "7978d9cc2a3813e31174bb026be18e7aa109ad81f32234daee592046c47221b7",
      "entries": 1
    },
    {
      "path": "World/HoE_DreamScene/Subregions/Hoe_Execution/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "92f8554116254c3ef1716edb66b327934b02022853a8f34da3bf7737e5f1e9d9",
      "entries": 12
    },
    {
      "path": "World/HoE_DreamScene/Subregions/HoE_Portal1/001_XMLs.dv2",
      "size": 32768,
      "sha256": "73dc4c6b4f51cb5cefe1c9a77eda159c358cb3e2c6326fa4e5dd53aedbd0971d",
      "entries": 11
    },
    {
      "path": "World/HoE_DreamScene/Subregions/HoE_Portal1/003_Static.dv2",
      "size": 1081344,
      "sha256": "4a6848f37d710a6fe262fb63600f7f3bb145379b4122b1602f5f12f5afa432ec",
      "entries": 17
    },
    {
      "path": "World/HoE_DreamScene/Subregions/HoE_Portal1/004_StaticMeshes.dv2",
      "size": 8781824,
      "sha256": "28e0e7edfc2c6ba7c25996a939205f9d62273803ea3cf02786d524b978b81103",
      "entries": 1
    },
    {
      "path": "World/HoE_DreamScene/Subregions/HoE_Portal1/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "5fa8d8ef523be466b59ed8b3f98738be6bdb92b3da7b0270c423bcd06eebf7a4",
      "entries": 12
    },
    {
      "path": "World/MaxosTemple/Main/001_XMLs.dv2",
      "size": 98304,
      "sha256": "59adcc3294d3b0340a4f3f8041e5993bc158b4abec3efca826cae61aeff0b3bc",
      "entries": 15
    },
    {
      "path": "World/MaxosTemple/Main/003_Static.dv2",
      "size": 1245184,
      "sha256": "18eec6966f76f0927e0af5c4381862ed6e921aabaa86636f1a7ac9179ee50ba5",
      "entries": 12
    },
    {
      "path": "World/MaxosTemple/Main/004_StaticMeshes.dv2",
      "size": 22020096,
      "sha256": "eea6d2f06730625253fae60b57b02506ebdead1c98629f439c59317b6f7f913e",
      "entries": 1
    },
    {
      "path": "World/MaxosTemple/Main/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "c9d491904fb145109a3aa24205fc21e76507e5ee756bee6137daebfd2f2e0e6e",
      "entries": 12
    },
    {
      "path": "World/RiverTown_FF/Main/001_XMLs.dv2",
      "size": 65536,
      "sha256": "f2595a7efc297399de09fb91ec3395db24e9b11eaf6a12575f88c37cda4f5da5",
      "entries": 19
    },
    {
      "path": "World/RiverTown_FF/Main/003_Static.dv2",
      "size": 2555904,
      "sha256": "cd6c236c32816b4f18208037f6615e4534a7ea7da30b5221fd321f67d1b5167c",
      "entries": 37
    },
    {
      "path": "World/RiverTown_FF/Main/004_StaticMeshes.dv2",
      "size": 393216,
      "sha256": "8bbba381b4b3dd4e4ff4ebfa8a9134411c62154d8ebad41f1bd789977984dae2",
      "entries": 1
    },
    {
      "path": "World/RiverTown_FF/Main/005_Streamable.dv2",
      "size": 4915200,
      "sha256": "5b389ab66026db5575b07822df130b866ed5d27074f97316d49c16360de0713a",
      "entries": 32
    },
    {
      "path": "World/RiverTown_FF/Main/006_StreamableInMemory.dv2",
      "size": 557056,
      "sha256": "e73fe7d0a08837bca4437d842e22b3f949476afb9c334d42c073dc8db9c2ec3e",
      "entries": 297
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali/001_XMLs.dv2",
      "size": 32768,
      "sha256": "c0559eaf6d1982e661bee56fe9f231c1ce45d92823896e15808c2d3a4b03a927",
      "entries": 15
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali/003_Static.dv2",
      "size": 655360,
      "sha256": "a910612cda3ce15db9445c15b63d82ca017c00594b34ad841ee8060f8e838e03",
      "entries": 10
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali/004_StaticMeshes.dv2",
      "size": 1540096,
      "sha256": "f303f4b6f2f9f3e12c91cdcf9a337b2e2e3edce219f12f32f0929a2f561646dc",
      "entries": 1
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "d8953f92f4b885f99279eb44ca2730c03ff20626d7b28e3fa63d0f726fcd0559",
      "entries": 12
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali_Mini/001_XMLs.dv2",
      "size": 32768,
      "sha256": "fab2d3f336585895faeaff2628599d7537dab1a70046d87063269cecca2ab16d",
      "entries": 15
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali_Mini/003_Static.dv2",
      "size": 655360,
      "sha256": "f740002f462e050d45d9bb7122ed7f85e9993248e3c713aa93a65adaeebf9854",
      "entries": 10
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali_Mini/004_StaticMeshes.dv2",
      "size": 1146880,
      "sha256": "809b45dc8d1ed3e2621138b6c5d95c2de446e3c9f244e98e9ecd82ebf448bdaf",
      "entries": 1
    },
    {
      "path": "World/RiverTown_FF/Subregions/FF_Kali_Mini/006_StreamableInMemory.dv2",
      "size": 65536,
      "sha256": "bae36201e6f7ecb014ce26dcebed525cae4842a9935596af868559964e5beaef",
      "entries": 12
    }
  ],
  "resources": [
    {
      "role": "beata",
      "logical_path": "Episodes\\Episode_2\\Dialogs\\Exp_AD_AlerothHealers_Poor2.xml",
      "source_archive": "Episode_2/DialogData.dv2",
      "source_sha256": "87270f173f24dbc35c76cd72dda72978215d5d4a5d470d66b81dd73d77f3228a",
      "source_size": 1310,
      "occurrences": [
        {
          "archive": "Episode_2/DialogData.dv2",
          "sha256": "87270f173f24dbc35c76cd72dda72978215d5d4a5d470d66b81dd73d77f3228a",
          "size": 1310
        }
      ]
    },
    {
      "role": "hansel",
      "logical_path": "Episodes\\Episode_2\\Dialogs\\Exp_AL_Hansel.xml",
      "source_archive": "Patch.dv2",
      "source_sha256": "81bfc433861cc98743edd0375d4597667e36eb1ec88333678ff328f73ead9a22",
      "source_size": 35592,
      "occurrences": [
        {
          "archive": "Episode_2/DialogData.dv2",
          "sha256": "d127cc9991e045cf317b23ebce58504f49feb91a0597bf65d8546f14d2dca9b3",
          "size": 39530
        },
        {
          "archive": "Patch.dv2",
          "sha256": "81bfc433861cc98743edd0375d4597667e36eb1ec88333678ff328f73ead9a22",
          "size": 35592
        }
      ]
    },
    {
      "role": "quests",
      "logical_path": "Episodes\\Episode_2\\rpgstats_questprototypes.xml",
      "source_archive": "MainDataStartup.dv2",
      "source_sha256": "0cbeeb1d043c7c4f64cc287d4aab1d53afcddfc766b22f911f9dc02a09bd6dcc",
      "source_size": 225698,
      "occurrences": [
        {
          "archive": "MainDataStartup.dv2",
          "sha256": "0cbeeb1d043c7c4f64cc287d4aab1d53afcddfc766b22f911f9dc02a09bd6dcc",
          "size": 225698
        }
      ]
    },
    {
      "role": "events",
      "logical_path": "Episodes\\Episode_2\\story\\globalevents.xml",
      "source_archive": "MainDataStub.dv2",
      "source_sha256": "b0df8e6c16ddca3b6126b8d9c2e95c87aae2ecc0eae9d1a4565fe0b802f84705",
      "source_size": 81535,
      "occurrences": [
        {
          "archive": "MainDataStub.dv2",
          "sha256": "b0df8e6c16ddca3b6126b8d9c2e95c87aae2ecc0eae9d1a4565fe0b802f84705",
          "size": 81535
        }
      ]
    },
    {
      "role": "seed",
      "logical_path": "Win32\\Episodes\\Episode_2\\Story\\init_savegame.dsg",
      "source_archive": "Patch.dv2",
      "source_sha256": "787eb0cd3918608ecf8fc025943b47b406a79c03427342d06136df240acc56e2",
      "source_size": 621569,
      "occurrences": [
        {
          "archive": "Episode_2/InitSaveGame.dv2",
          "sha256": "34dd19fc7b204b2540ff3338cbfc1c2d5f9720eae3c3268c89c5ad86e0c02c43",
          "size": 623775
        },
        {
          "archive": "Patch.dv2",
          "sha256": "787eb0cd3918608ecf8fc025943b47b406a79c03427342d06136df240acc56e2",
          "size": 621569
        }
      ]
    }
  ]
}


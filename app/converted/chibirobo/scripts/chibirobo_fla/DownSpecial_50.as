package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class DownSpecial_50 extends MovieClip
    {

        public var counterBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;
        public var proj:*;
        public var projLinkage:*;
        public var frameLabel:*;
        public var xScale:*;
        public var yScale:*;
        public var metadata:*;
        public var itemChar:*;

        public function DownSpecial_50()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 16, this.frame17, 17, this.frame18, 27, this.frame28, 29, this.frame30, 31, this.frame32, 32, this.frame33, 33, this.frame34, 34, this.frame35, 35, this.frame36, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 41, this.frame42, 44, this.frame45, 46, this.frame47, 49, this.frame50, 50, this.frame51, 60, this.frame61, 62, this.frame63, 64, this.frame65, 65, this.frame66, 66, this.frame67, 67, this.frame68, 68, this.frame69, 69, this.frame70, 70, this.frame71, 71, this.frame72, 73, this.frame74, 76, this.frame77, 78, this.frame79, 81, this.frame82);
        }

        public function getChibiProjectile(_arg_1:*):void
        {
            if (this.proj)
            {
                return;
            };
            this.proj = _arg_1.data.receiver;
            if (!this.checkPocketable())
            {
                this.proj = null;
                return;
            };
            SSF2API.print(((this.proj + " is a(n) ") + this.proj.getType()));
            if (this.proj.getType() === "SSF2Projectile")
            {
                this.self.removeEventListener(SSF2Event.CHAR_COUNTER, this.getChibiProjectile);
                SSF2API.print("Got it!");
                this.self.stancePlayFrame("store");
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                this.self.removeEventListener(SSF2Event.CHAR_COUNTER, this.getChibiProjectile);
                SSF2API.print("Got it!");
                this.self.stancePlayFrame("store_item");
            };
        }

        public function checkPocketable():Boolean
        {
            var _local_1:* = undefined;
            var _local_2:* = undefined;
            if (!(this.proj) || this.proj.isDisposed())
            {
                return false;
            }
            else
            if (this.proj.getType() === "SSF2Projectile")
            {
                _local_1 = this.proj.getProjectileStat("linkage_id");
                if (!(this.proj.getProjectileStat("canBePocketed")) || (this.proj.getID() == -1) || (this.proj.getID() == this.self.getID()) || (_local_1 == "yoshi_fireball") || (_local_1 == "Yoshi_fireball") || (_local_1 == "p1") || (_local_1 == "p15") || (_local_1 == "p2") || (_local_1 == "dragon") || (_local_1 == "warioman_bomb") || (_local_1 == "HUGEBOOM"))
                {
                    return false;
                };
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                _local_2 = this.proj.getItemStat("linkage_id");
                if ((this.proj.getID() == -1) || (this.proj.getID() == this.self.getID()) || (_local_2 == "delibird_bomb"))
                {
                    return false;
                };
            }
            else
            {
                return false;
            }
            else
            {
            return true;
            };
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function onHurtInterrupt(_arg_1:Object):Boolean
        {
            if (this.proj && !(this.proj.isDisposed()) && (_arg_1.target === this.proj))
            {
                return true;
            };
            return false;
        }

        public function onStateChange(_arg_1:*):void
        {
            this.self.setHurtInterrupt(null);
        }

        public function onDestroy(_arg_1:*):void
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.destroy();
            };
        }

        public function animateProj():void
        {
            if ((this.self.getHitBox("touchBox") != null) && !(this.proj.isDisposed()))
            {
                this.proj.setX((this.self.getX() + this.flipX(this.self.getHitBox("touchBox").x)));
                this.proj.setY((this.self.getY() + this.self.getHitBox("touchBox").y));
            };
        }

        public function canSuspend():Boolean
        {
            switch (this.projLinkage)
            {
                case "dee_nspec":
                case "dee_spear":
                case "BMfsmashfull":
                case "BMdsmashfull":
                case "bmmeteorprojectile":
                case "bm_waterSpout":
                case "fireBreath":
                case "fireBreathBlue":
                case "fireBreathPurple":
                case "chibi_lazor":
                case "dedede_gordo":
                case "dedede_jump_star":
                case "falco_laser":
                case "falco_uthrowlaser":
                case "lazor":
                case "UThrowLaser":
                case "bacon":
                case "getsuga2":
                case "isaac_move_proj":
                case "isaac_scoop_effect":
                case "isaac_utilt_proj":
                case "isaac_dtilt_proj":
                case "isaac_gaia_proj":
                case "kirby_swordwave":
                case "kirby_dice":
                case "krystal_snipe":
                case "krystal_grenade_proj":
                case "link_arrow":
                case "bombArrow":
                case "linkBoomerang":
                case "lloyd_wave":
                case "aura_sphere":
                case "luigi_fireball_wrapper":
                case "mario_fireball":
                case "beat_call":
                case "mm_quickboomerang":
                case "megaman_bullet":
                case "megaman_bullet2":
                case "megaman_bullet3":
                case "megaman_blastshot":
                case "megaman_crashbomb":
                case "megaman_waterwave":
                case "hardknuckle":
                case "mm_tornado_proj":
                case "naruto_rasenganexplosionground":
                case "rasenshuriken":
                case "naruto_fallclone":
                case "naruto_shadow":
                case "naruto_clone2":
                case "naruto_clone":
                case "fthrow_shuriken":
                case "ness_pkthunderproj":
                case "ness_pkfireproj":
                case "pacman_watershot":
                case "pacman_hydrant_proj":
                case "pichuthunderJolt2":
                case "pichuthunder":
                case "thunderJolt2":
                case "thunder":
                case "pit_arrow2":
                case "rayman_vortexProj":
                case "hadoken":
                case "command_hadoken":
                case "shakunetsu_hadoken":
                case "samus_chargeshot":
                case "samus_missile":
                case "samus_supermissile":
                case "samus_bomb":
                case "needle":
                case "air_needle":
                case "axe":
                case "cross_boomerang":
                case "water":
                case "springidle":
                case "sora_blizzardproj":
                case "tails_b_v2":
                case "waluigi_dice":
                case "waluigi_pot":
                case "eggBomb":
                case "dspecstars":
                case "zamus_pshot_weak":
                case "zamus_pshot_strong":
                case "starrod_star":
                case "starrod_star_weak":
                case "beamrod_star":
                case "rayGun_bullet":
                case "coconutGun_bullet":
                case "fireFlower_proj":
                case "iceFlower_proj":
                case "firework_proj":
                case "bullet_bill_projectile":
                case "hammerBro_hammer":
                case "destructodisc":
                case "spiny":
                case "magnetbomber_bomb":
                case "rinka":
                case "protoman_shot":
                case "protoman_chargeblast":
                case "pk_beam_omega":
                case "pk_beam_gamma":
                case "blastoise_pump":
                case "chikorita_leaf":
                case "dracometeor":
                case "onix_rock":
                case "seedotseed":
                case "snivy_leaf":
                case "staryu_star":
                    return true;
                case 107:
                default:
                    return false;
                    break;
            }
        }

        public function charItemIdentifier():String
        {
            switch (this.projLinkage)
            {
                case "link_bomb":
                    return "link";
                case "pacman_cherry":
                case "pacman_strawberry":
                case "pacman_orange":
                case "pacman_apple":
                case "pacman_melon":
                case "pacman_galaxian":
                case "pacman_bell":
                case "pacman_key":
                    return "pacman";
                case "smile":
                case "stitch":
                case "kissy":
                case "angry":
                case "crying":
                case "eh":
                case "happy":
                case "turnip_shock":
                case "whatever":
                case "ODDISH":
                    return "peach";
                case 19:
                default:
                    return null;
                    break;
            }
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.proj = null;
            this.projLinkage = null;
            this.frameLabel = null;
            this.xScale = 1;
            this.yScale = 1;
            if (this.self && SSF2API.isReady())
            {
                if (this.self.getGlobalVariable("chibiProjGlobal") != null)
                {
                    this.self.stancePlayFrame("fire");
                }
                else if (this.self.getGlobalVariable("chibiItemGlobal") != null)
                {
                    this.self.stancePlayFrame("fire_item");
                }
                else
                {
                    this.self.addEventListener(SSF2Event.CHAR_COUNTER, this.getChibiProjectile);
                };
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_light");
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-30
            });
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_swirl");
            this.self.setIntangibility(true);
            this.self.setHurtInterrupt(this.onHurtInterrupt);
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.updateProjectileStats({"suspend":true});
                this.projLinkage = this.proj.getProjectileStat("linkage_id");
                if (this.canSuspend())
                {
                    this.proj.stancePlayFrame("suspend");
                };
                if (this.projLinkage == "sora_strikeraidproj")
                {
                    this.proj.destroy();
                }
                else
                {
                    switch (this.projLinkage)
                    {
                    case "bmmeteorprojectile":
                    this.self.setGlobalVariable("chibiProjMetadata", {"dmg":this.proj.getAttackBoxStat(1, "damage")});
                    break;
                    case "bacon":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "pal":this.proj.getPaletteSwapData(),
                        "pri":this.proj.getAttackBoxStat(1, "priority")
                    });
                    break;
                    case "regi_rock":
                    this.self.setGlobalVariable("DDDProjMetadata", {
                        "curType":this.proj.getStanceMC().curType,
                        "rfr":this.proj.getAttackStat("refreshRate"),
                        "pri":this.proj.getAttackBoxStat(1, "priority"),
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "wkb":this.proj.getAttackBoxStat(1, "weightKB"),
                        "kbg":this.proj.getAttackBoxStat(1, "kbConstant"),
                        "dir":this.proj.getAttackBoxStat(1, "direction")
                    });
                    break;
                    case "getsuga2":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "rfr":this.proj.getAttackStat("refreshRate"),
                        "pri":this.proj.getAttackBoxStat(1, "priority"),
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "wkb":this.proj.getAttackBoxStat(1, "weightKB"),
                        "kbg":this.proj.getAttackBoxStat(1, "kbConstant"),
                        "dir":this.proj.getAttackBoxStat(1, "direction"),
                        "spd":this.proj.getProjectileStat("xspeed")
                    });
                    break;
                    case "krystal_snipe":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                    });
                    break;
                    case "link_arrow":
                    case "bombArrow":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "pal":this.proj.getPaletteSwapData(),
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "spd":this.proj.getProjectileStat("xspeed")
                    });
                    break;
                    case "kirby_dice":
                    case "linkBoomerang":
                    case "beat_call":
                    case "megaman_crashbomb":
                    case "naruto_fallclone":
                    case "naruto_shadow":
                    case "naruto_clone2":
                    case "naruto_clone":
                    case "pacman_hydrant_proj":
                    case "cross_boomerang":
                    case "waluigi_dice":
                    case "waluigi_pot":
                    case "eggBomb":
                    this.self.setGlobalVariable("chibiProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                    break;
                    case "aura_sphere":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "kbg":this.proj.getAttackBoxStat(1, "kbConstant"),
                        "spd":this.proj.getProjectileStat("xspeed")
                    });
                    break;
                    case "hardknuckle":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "pal":this.proj.getPaletteSwapData()
                    });
                    break;
                    case "naruto_rasenganexplosionground":
                    this.self.setGlobalVariable("chibiProjMetadata", {"dmg":this.proj.getAttackBoxStat(2, "damage")});
                    break;
                    case "pichuthunderJolt2":
                    this.self.setGlobalVariable("chibiProjMetadata", {"prl":this.proj.getAttackBoxStat(1, "paralysis")});
                    break;
                    case "pit_arrow2":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "pal":this.proj.getStanceMC().altTrail
                    });
                    break;
                    case "hadoken":
                    case "command_hadoken":
                    case "shakunetsu_hadoken":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "spd":this.proj.getProjectileStat("xspeed"),
                        "tmx":this.proj.getProjectileStat("time_max")
                    });
                    break;
                    case "samus_chargeshot":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "bkb":this.proj.getAttackBoxStat(1, "power"),
                        "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                    });
                    break;
                    case "zamus_pshot_weak":
                    this.self.setGlobalVariable("chibiProjMetadata", {
                        "dmg":this.proj.getAttackBoxStat(1, "damage"),
                        "prl":this.proj.getAttackBoxStat(1, "paralysis")
                    });
                    break;
                    case 30:
                    default:
                    break;
                    }
                    this.self.createTimer(1, 0, this.animateProj);
                    this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
                };
            };
        }

        internal function frame28():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(5),
                "y":-46,
                "parentLock":true
            });
        }

        internal function frame30():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.self.setGlobalVariable("chibiProjGlobal", this.proj.exportStats());
                this.self.getGlobalVariable("telly").getStanceMC().hasProjectile = true;
            };
            this.self.setIntangibility(false);
        }

        internal function frame32():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.xScale = this.proj.getXScale();
                this.yScale = this.proj.getYScale();
                if (!this.proj.isFacingRight())
                {
                    this.xScale *= -1;
                };
            };
            this.self.setGlobalVariable("xScale", this.xScale);
            this.self.setGlobalVariable("yScale", this.yScale);
        }

        internal function frame33():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale * 0.5), (this.yScale * 0.5));
            };
        }

        internal function frame34():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale * 0.25), (this.yScale * 0.25));
            };
        }

        internal function frame35():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            this.self.setHurtInterrupt(null);
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.destroy();
            };
        }

        internal function frame36():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(3.5),
                "y":-36
            });
        }

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(8),
                "y":-46
            });
            this.proj = this.self.fireProjectile(this.self.getGlobalVariable("chibiProjGlobal"));
            if (!(this.proj) || this.proj.isDisposed())
            {
                SSF2API.print("Projectile throw unsuccessful.");
                this.self.setGlobalVariable("chibiProjGlobal", null);
                this.self.setGlobalVariable("chibiProjMetadata", null);
                this.self.stancePlayFrame("search");
                return;
            };
            this.proj.updateProjectileStats({"suspend":true});
            this.projLinkage = this.proj.getProjectileStat("linkage_id");
            if (this.canSuspend())
            {
                this.proj.stancePlayFrame("suspend");
            };
            this.xScale = this.self.getGlobalVariable("xScale");
            this.yScale = this.self.getGlobalVariable("yScale");
            if ((this.self.isFacingRight() && (this.xScale < 0)) || (!(this.self.isFacingRight()) && (this.xScale > 0)))
            {
                this.xScale *= -1;
            };
            this.metadata = this.self.getGlobalVariable("chibiProjMetadata");
            if (this.metadata != null)
            {
                switch (this.self.getGlobalVariable("chibiProjGlobal").linkage_id)
                {
                case "bmmeteorprojectile":
                this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                break;
                case "bacon":
                this.proj.setPaletteSwapData(this.metadata.pal);
                this.proj.updateAttackBoxStats(1, {"priority":this.metadata.pri});
                break;
                case "regi_rock":
                this.proj.getStanceMC().self = this.proj;
                this.proj.getStanceMC().curType = this.metadata.curType;
                this.proj.updateProjectileStats({"ghost":true});
                this.proj.stancePlayFrame(("SPEEN_" + this.metadata.curType));
                this.proj.updateAttackBoxStats(1, {
                    "priority":this.metadata.pri,
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "weightKB":this.metadata.wkb,
                    "kbConstant":this.metadata.kbg,
                    "direction":this.metadata.dir
                });
                case "getsuga2":
                this.proj.updateAttackStats({"refreshRate":this.metadata.rfr});
                this.proj.updateAttackBoxStats(1, {
                    "priority":this.metadata.pri,
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "weightKB":this.metadata.wkb,
                    "kbConstant":this.metadata.kbg,
                    "direction":this.metadata.dir
                });
                this.proj.updateProjectileStats({"xspeed":this.metadata.spd});
                this.proj.setXSpeed(this.metadata.spd, false);
                break;
                case "krystal_snipe":
                this.proj.updateAttackBoxStats(1, {
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "kbConstant":this.metadata.kbg
                });
                break;
                case "link_arrow":
                case "bombArrow":
                this.proj.setPaletteSwapData(this.metadata.pal);
                this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                this.proj.updateProjectileStats({"xspeed":this.metadata.spd});
                this.proj.setXSpeed(this.metadata.spd, false);
                break;
                case "kirby_dice":
                case "linkBoomerang":
                case "beat_call":
                case "megaman_crashbomb":
                case "naruto_fallclone":
                case "naruto_shadow":
                case "naruto_clone2":
                case "naruto_clone":
                case "pacman_hydrant_proj":
                case "cross_boomerang":
                case "waluigi_dice":
                case "waluigi_pot":
                case "eggBomb":
                this.proj.setPaletteSwapData(this.metadata.pal);
                break;
                case "aura_sphere":
                this.proj.updateAttackBoxStats(1, {
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "kbConstant":this.metadata.kbg
                });
                this.proj.updateAttackBoxStats(2, {
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "kbConstant":this.metadata.kbg
                });
                this.proj.updateProjectileStats({"xspeed":this.metadata.spd});
                this.proj.setXSpeed(this.metadata.spd, false);
                break;
                case "hardknuckle":
                this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                this.proj.setPaletteSwapData(this.metadata.pal);
                break;
                case "naruto_rasenganexplosionground":
                this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                this.proj.updateAttackBoxStats(2, {"damage":this.metadata.dmg});
                break;
                case "pichuthunderJolt2":
                this.proj.updateAttackBoxStats(1, {"paralysis":this.metadata.prl});
                break;
                case "pit_arrow2":
                this.proj.updateAttackBoxStats(1, {
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb
                });
                this.proj.getStanceMC().altTrail = this.metadata.pal;
                SSF2Utils.setColorFilters(this.proj.getMC(), {
                    "hue":-60,
                    "redMultiplier":-1,
                    "greenMultiplier":-1,
                    "blueMultiplier":-1,
                    "redOffset":255,
                    "greenOffset":255,
                    "blueOffset":255
                });
                break;
                case "hadoken":
                case "command_hadoken":
                case "shakunetsu_hadoken":
                this.proj.updateProjectileStats({
                    "xspeed":this.metadata.spd,
                    "time_max":this.metadata.tmx
                });
                this.proj.setXSpeed(this.metadata.spd, false);
                break;
                case "samus_chargeshot":
                this.proj.updateAttackBoxStats(1, {
                    "damage":this.metadata.dmg,
                    "power":this.metadata.bkb,
                    "kbConstant":this.metadata.kbg
                });
                break;
                case "zamus_pshot_weak":
                this.proj.updateAttackBoxStats(1, {
                    "damage":this.metadata.dmg,
                    "paralysis":this.metadata.prl
                });
                break;
                case 30:
                default:
                break;
                }
            };
            this.self.getGlobalVariable("telly").getStanceMC().hasProjectile = false;
            SSF2API.print("Successfully threw projectile back.");
            this.self.setGlobalVariable("chibiProjGlobal", null);
            this.self.setGlobalVariable("chibiProjMetadata", null);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
            this.proj.setScale(((this.xScale * 0.5) / this.self.getScale().x), ((this.yScale * 0.5) / this.self.getScale().y));
            this.self.createTimer(1, 0, this.animateProj);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-30
            });
        }

        internal function frame39():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale(((this.xScale * 0.75) / this.self.getScale().x), ((this.yScale * 0.75) / this.self.getScale().y));
            };
        }

        internal function frame40():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale / this.self.getScale().x), (this.yScale / this.self.getScale().y));
            };
        }

        internal function frame42():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(-8),
                "y":-39
            });
        }

        internal function frame45():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame47():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            this.self.destroyTimer(this.animateProj);
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.updateProjectileStats({
                    "rotate":true,
                    "suspend":false
                });
                if (this.canSuspend())
                {
                    this.proj.stancePlayFrame("chibi");
                };
                switch (this.projLinkage)
                {
                case "dee_spear":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.setYSpeed(-9);
                this.proj.setXSpeed(12, false);
                break;
                case "BMfsmashfull":
                case "dedede_jump_star":
                case "dspecstars":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "BMdsmashfull":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(25), 0);
                break;
                case "bmmeteorprojectile":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.updateProjectileStats({
                    "xdecay":0,
                    "xspeed":4,
                    "yspeed":0,
                    "gravity":0.5,
                    "maxgravity":5
                });
                this.proj.angleControl(9, 60);
                this.proj.angleControl(9, 120);
                this.proj.updateProjectileStats({"maxgravity":9});
                this.proj.angleControl(9, 315);
                this.proj.angleControl(9, 225);
                break;
                case "bm_waterSpout":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.updateAttackBoxStats(1, {"direction":30});
                this.proj.angleControl(11.7, 0);
                this.proj.angleControl(11.7, 180);
                break;
                case "falco_uthrowlaser":
                case "UThrowLaser":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.updateAttackBoxStats(1, {
                    "reversableAngle":false,
                    "direction":0
                });
                this.proj.angleControl(20, 0);
                this.proj.angleControl(20, 180);
                break;
                case "bacon":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.angleControl(12, SSF2API.randomInteger(45, 80));
                this.proj.angleControl(12, (180 - SSF2API.randomInteger(45, 80)));
                break;
                case "getsuga2":
                case "isaac_move_proj":
                case "kirby_swordwave":
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "isaac_utilt_proj":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(25), 0);
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "isaac_dtilt_proj":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(8), 0);
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "isaac_gaia_proj":
                this.proj.updateProjectileStats({
                    "rotate":false,
                    "gravity":0,
                    "maxgravity":0
                });
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(50), 0);
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "dedede_gordo":
                case "kirby_dice":
                case "lloyd_wave":
                case "aura_sphere":
                case "mm_tornado_proj":
                case "naruto_rasenganexplosionground":
                case "rasenshuriken":
                case "naruto_fallclone":
                case "naruto_shadow":
                case "pichuthunder":
                case "thunderJolt2":
                case "thunder":
                case "samus_chargeshot":
                case "needle":
                case "air_needle":
                case "waluigi_dice":
                case "magnetbomber_bomb":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "luigi_fireball_wrapper":
                case "mario_fireball":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY((this.self.getY() - 20));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(22), 0);
                break;
                case "beat_call":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(30), 0);
                break;
                case "mm_quickboomerang":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(10), 0);
                break;
                case "megaman_bullet":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY((this.self.getY() - 20));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(10), 0);
                break;
                case "megaman_bullet2":
                case "megaman_bullet3":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY((this.self.getY() - 20));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(19), 0);
                break;
                case "megaman_blastshot":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY((this.self.getY() - 20));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(30), 0);
                break;
                case "hardknuckle":
                this.proj.setY((this.self.getY() - 20));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "naruto_clone2":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "naruto_clone":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(30), 0);
                break;
                case "ness_pkthunderproj":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.setXSpeed(9, false);
                this.proj.setYSpeed(0);
                break;
                case "ness_pkfireproj":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.angleControl(14, 356);
                this.proj.angleControl(14, 184);
                this.proj.angleControl(14, 320);
                this.proj.angleControl(14, 220);
                break;
                case "pacman_watershot":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(30), 0);
                break;
                case "pacman_hydrant_proj":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.setXSpeed(12, false);
                this.proj.setYSpeed(-12);
                break;
                case "pichuthunderJolt2":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.angleControl(4.5, 20);
                this.proj.angleControl(4.5, 160);
                break;
                case "rayman_vortexProj":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY(this.self.getY());
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                break;
                case "hadoken":
                case "command_hadoken":
                case "shakunetsu_hadoken":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setY((this.self.getY() - 13));
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "samus_bomb":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.angleControl(10, 20);
                this.proj.angleControl(10, 160);
                break;
                case "axe":
                case "cross_boomerang":
                case "springidle":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                break;
                case "water":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                case "sora_blizzardproj":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.setXSpeed(35, false);
                break;
                case "tails_b_v2":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.setXSpeed(6, false);
                this.proj.setYSpeed(0);
                this.proj.setXSpeed(4, false);
                this.proj.setYSpeed(4);
                break;
                case "waluigi_pot":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.setY(this.self.getY());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.safeMove(0, 6);
                this.proj.setYSpeed(this.self.getYSpeed());
                break;
                case "eggBomb":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.angleControl(9, 60);
                this.proj.angleControl(9, 120);
                break;
                case "spiny":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.angleControl(9, 60);
                this.proj.angleControl(9, 120);
                break;
                case "rinka":
                this.proj.updateProjectileStats({"rotate":false});
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.angleControl(10, 20);
                this.proj.angleControl(10, 160);
                this.proj.angleControl(10, 330);
                this.proj.angleControl(10, 210);
                break;
                case "protoman_shot":
                case "protoman_chargeblast":
                this.proj.updateProjectileStats({"rotate":false});
                break;
                case "pk_beam_omega":
                this.proj.setX(this.self.getX());
                this.proj.setY(this.self.getY());
                this.proj.angleControl(-20, (20 + 180));
                this.proj.angleControl(-20, (160 + 180));
                this.proj.angleControl(-20, (330 + 180));
                this.proj.angleControl(-20, (210 + 180));
                break;
                case "pk_beam_gamma":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.setXSpeed(20, false);
                break;
                case "dracometeor":
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                this.proj.updateProjectileStats({"gravity":1});
                this.proj.angleControl(20, 30);
                this.proj.angleControl(20, 150);
                this.proj.angleControl(20, 315);
                this.proj.angleControl(20, 225);
                break;
                case "onix_rock":
                case "regi_rock":
                this.proj.updateProjectileStats({
                    "gravity":1,
                    "rotate":false
                });
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(20), 0);
                this.proj.angleControl(10, 35);
                this.proj.angleControl(10, 145);
                this.proj.setYSpeed(5);
                break;
                case 71:
                default:
                this.proj.setX(this.self.getX());
                this.proj.safeMove(this.flipX(15), 0);
                break;
                }
            };
            if (this.proj && !(this.proj.isDisposed()) && (this.projLinkage == "naruto_clone2"))
            {
                this.proj.angleControl(80, 270);
            };
            if (this.proj && !(this.proj.isDisposed()) && (this.projLinkage == "naruto_clone"))
            {
                this.proj.updateProjectileStats({"rotate":false});
            };
            if (this.proj && !(this.proj.isDisposed()) && this.frameLabel)
            {
                this.proj.stancePlayFrame(this.frameLabel);
            };
        }

        internal function frame50():*
        {
            this.self.endAttack();
        }

        internal function frame51():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_swirl");
            this.self.setIntangibility(true);
            this.self.setHurtInterrupt(this.onHurtInterrupt);
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.toHeld();
                this.projLinkage = this.proj.getItemStat("linkage_id");
                switch (this.projLinkage)
                {
                case "link_bomb":
                this.self.setGlobalVariable("chibiProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                break;
                case "medusahead":
                this.proj.dispose();
                break;
                case 2:
                default:
                break;
                }
                this.self.createTimer(1, 0, this.animateProj);
                this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
            };
        }

        internal function frame61():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(5),
                "y":-46,
                "parentLock":true
            });
        }

        internal function frame63():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.self.setGlobalVariable("chibiItemGlobal", {
                    "nme":this.projLinkage,
                    "chr":this.charItemIdentifier()
                });
                this.self.getGlobalVariable("telly").getStanceMC().hasProjectile = true;
            };
            this.self.setIntangibility(false);
        }

        internal function frame65():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.xScale = this.proj.getXScale();
                this.yScale = this.proj.getYScale();
                if (!this.proj.isFacingRight())
                {
                    this.xScale *= -1;
                };
            };
            this.self.setGlobalVariable("xScale", this.xScale);
            this.self.setGlobalVariable("yScale", this.yScale);
        }

        internal function frame66():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale * 0.5), (this.yScale * 0.5));
            };
        }

        internal function frame67():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale * 0.25), (this.yScale * 0.25));
            };
        }

        internal function frame68():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(3.5),
                "y":-36
            });
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            this.self.setHurtInterrupt(null);
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.dispose();
                this.proj.destroy();
            };
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }

        internal function frame70():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(8),
                "y":-46
            });
            this.projLinkage = this.self.getGlobalVariable("chibiItemGlobal").nme;
            SSF2API.print(this.projLinkage);
            if (this.projLinkage == null)
            {
                SSF2API.print("Item throw unsuccessful.");
                this.self.setGlobalVariable("chibiItemGlobal", null);
                this.self.setGlobalVariable("chibiProjMetadata", null);
                this.self.stancePlayFrame("search");
                return;
            };
            this.itemChar = this.self.getGlobalVariable("chibiItemGlobal").chr;
            if (this.itemChar != null)
            {
                this.proj = this.self.generateCharacterItem(this.projLinkage, this.itemChar, true);
            }
            else
            {
                this.proj = this.self.generateItem(this.projLinkage, true, false, true);
            };
            if (!(this.proj) || this.proj.isDisposed())
            {
                SSF2API.print("Item throw unsuccessful.");
                this.self.setGlobalVariable("chibiItemGlobal", null);
                this.self.setGlobalVariable("chibiProjMetadata", null);
                this.self.stancePlayFrame("search");
                return;
            };
            this.xScale = this.self.getGlobalVariable("xScale");
            this.yScale = this.self.getGlobalVariable("yScale");
            if ((this.self.isFacingRight() && (this.xScale < 0)) || (!(this.self.isFacingRight()) && (this.xScale > 0)))
            {
                this.xScale *= -1;
            };
            this.metadata = this.self.getGlobalVariable("chibiProjMetadata");
            if (this.metadata != null)
            {
                switch (this.projLinkage)
                {
                case "link_bomb":
                this.proj.setPaletteSwapData(this.metadata.pal);
                break;
                case 1:
                default:
                break;
                }
            };
            this.self.getGlobalVariable("telly").getStanceMC().hasProjectile = false;
            SSF2API.print("Successfully threw item back.");
            this.self.setGlobalVariable("chibiItemGlobal", null);
            this.self.setGlobalVariable("chibiProjMetadata", null);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
            this.proj.setScale(((this.xScale * 0.5) / this.self.getScale().x), ((this.yScale * 0.5) / this.self.getScale().y));
            this.self.createTimer(1, 0, this.animateProj);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-30
            });
        }

        internal function frame71():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale(((this.xScale * 0.75) / this.self.getScale().x), ((this.yScale * 0.75) / this.self.getScale().y));
            };
        }

        internal function frame72():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale((this.xScale / this.self.getScale().x), (this.yScale / this.self.getScale().y));
            };
        }

        internal function frame74():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(-8),
                "y":-39
            });
        }

        internal function frame77():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame79():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            this.self.destroyTimer(this.animateProj);
            if (this.proj && !(this.proj.isDisposed()))
            {
            };
        }

        internal function frame82():*
        {
            this.self.endAttack();
        }


    }
}


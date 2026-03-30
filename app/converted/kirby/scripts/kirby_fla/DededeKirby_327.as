package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DededeKirby_327 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var counterBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var continuePlaying:Boolean;
        public var handled:Boolean;
        public var sfxStop:Number;
        public var sfxStop2:Number;
        public var curFrame:int;
        public var proj:*;
        public var projLinkage:*;
        public var xScale:*;
        public var yScale:*;
        public var isOwnGordo:Boolean;
        public var xSpeedAir:int;
        public var xSpeedGround:int;
        public var fjmp_suck1:int;
        public var fjmp_suck2:int;
        public var fjmp_spit1:int;
        public var fjmp_spit2:int;
        public var itemChar:*;
        public var metadata:*;

        public function DededeKirby_327()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 13, this.frame14, 15, this.frame16, 18, this.frame19, 22, this.frame23, 23, this.frame24, 24, this.frame25, 33, this.frame34, 34, this.frame35, 37, this.frame38, 41, this.frame42, 49, this.frame50, 57, this.frame58, 58, this.frame59, 67, this.frame68, 68, this.frame69, 70, this.frame71, 84, this.frame85, 85, this.frame86, 87, this.frame88, 101, this.frame102, 102, this.frame103, 107, this.frame108, 108, this.frame109, 130, this.frame131, 131, this.frame132, 139, this.frame140, 146, this.frame147, 155, this.frame156, 163, this.frame164, 164, this.frame165, 169, this.frame170, 184, this.frame185, 185, this.frame186, 190, this.frame191, 191, this.frame192, 195, this.frame196, 196, this.frame197, 209, this.frame210, 210, this.frame211, 217, this.frame218, 218, this.frame219, 229, this.frame230, 230, this.frame231, 233, this.frame234, 240, this.frame241, 241, this.frame242, 253, this.frame254, 254, this.frame255, 257, this.frame258, 264, this.frame265, 265, this.frame266, 277, this.frame278);
        }

        public function toGroundSuck(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSuck);
            this.curFrame = (currentFrame - (this.fjmp_suck2 - this.fjmp_suck1));
            SSF2API.print(this.curFrame.toString());
            this.self.stancePlayFrame(this.curFrame);
        }

        public function getDDDProjectile(_arg_1:*):void
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
                this.self.removeEventListener(SSF2Event.CHAR_COUNTER, this.getDDDProjectile);
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                this.self.removeEventListener(SSF2Event.CHAR_COUNTER, this.getDDDProjectile);
            };
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSuck);
            var _local_2:* = "item_grab";
            if (!this.self.isOnGround())
            {
                _local_2 += "_air";
            };
            this.self.stancePlayFrame(_local_2);
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

        public function onDestroy(_arg_1:*):void
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.destroy();
            };
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

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function checkOwnGordo():void
        {
            var _local_1:* = null;
            if (!(this.self.gordo) || this.self.gordo.isDisposed())
            {
                return;
            }
            else
            if (SSF2API.hitboxTest(this.self, HitBoxType.COUNTER, this.self.gordo, HitBoxType.HIT).length > 0)
            {
                this.proj = this.self.gordo;
                this.isOwnGordo = true;
                this.self.setGlobalVariable("dddGlobal", this.proj.exportStats());
                _local_1 = "item_grab";
                if (!this.self.isOnGround())
                {
                    _local_1 += "_air";
                };
                this.self.stancePlayFrame(_local_1);
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
                this.self.destroyTimer(this.checkOwnGordo);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSuck);
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

        public function toGroundSpit(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSpit);
            this.curFrame = (currentFrame - (this.fjmp_spit2 - this.fjmp_spit1));
            SSF2API.print(this.curFrame.toString());
            this.self.stancePlayFrame(this.curFrame);
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

        public function toGroundItemAnim(_arg_1:*):void
        {
            gotoAndPlay((currentFrame - 21));
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundItemAnim);
        }

        internal function frame1():*
        {
            var _local_1:* = __activation__;
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.continuePlaying = false;
            this.handled = true;
            this.proj = null;
            this.projLinkage = null;
            this.xScale = 1;
            this.yScale = 1;
            this.isOwnGordo = false;
            if (SSF2API.isReady() && this.self)
            {
                this.xSpeedAir = this.self.getCharacterStat("max_xSpeed");
                this.xSpeedGround = 2;
                this.self.addEventListener(SSF2Event.CHAR_COUNTER, this.getDDDProjectile);
            };
            if (SSF2API.isReady() && this.self && (this.curFrame != currentFrame))
            {
                this.self.inhale.grabHook = function ():*
                {
                    self.removeEventListener(SSF2Event.GROUND_TOUCH, toGroundSuck);
                    self.playAttackSound(4);
                    SSF2API.stopSound(sfxStop);
                };
                this.self.inhale.cleanupHook = function ():*
                {
                    SSF2API.stopSound(sfxStop);
                };
                if (!this.self.isOnGround())
                {
                    this.fjmp_suck1 = currentFrame;
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSuck);
                    this.self.stancePlayFrame("airsuck");
                };
            };
        }

        internal function frame4():*
        {
            if (this.curFrame != currentFrame)
            {
                this.sfxStop = this.self.playAttackSound(1);
                this.self.setGlobalVariable("SlowCharge", null);
                this.self.attachEffect("global_dust_light");
                this.self.attachEffect("global_dust_heavy");
                this.self.inhale.start();
            };
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_dust_heavy");
            this.self.createTimer(1, -1, this.checkOwnGordo);
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame16():*
        {
            if (this.curFrame != currentFrame)
            {
                this.sfxStop2 = this.self.playAttackSound(2);
                SSF2API.stopSound(this.sfxStop);
            }
            else
            {
                this.curFrame = 0;
            };
            this.handled = false;
            this.continuePlaying = false;
        }

        internal function frame19():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame24():*
        {
            SSF2API.stopSound(this.sfxStop2);
            if (this.continuePlaying)
            {
                this.self.stancePlayFrame("suckagain");
            };
        }

        internal function frame25():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }

        internal function frame35():*
        {
            this.fjmp_suck2 = currentFrame;
        }

        internal function frame38():*
        {
            this.sfxStop = this.self.playAttackSound(1);
            this.self.setGlobalVariable("SlowCharge", null);
            this.self.attachEffect("global_dust_light");
            this.self.inhale.start();
        }

        internal function frame42():*
        {
            this.self.createTimer(1, -1, this.checkOwnGordo);
        }

        internal function frame50():*
        {
            this.sfxStop2 = this.self.playAttackSound(2);
            SSF2API.stopSound(this.sfxStop);
            this.handled = false;
            this.continuePlaying = false;
        }

        internal function frame58():*
        {
            SSF2API.stopSound(this.sfxStop2);
            if (this.continuePlaying)
            {
                this.self.stancePlayFrame("airsuckagain");
            };
        }

        internal function frame59():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }

        internal function frame69():*
        {
            this.fjmp_spit1 = currentFrame;
            if (!this.self.isOnGround())
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGroundSpit);
                this.self.stancePlayFrame("airspit");
            };
        }

        internal function frame71():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.attachEffect("global_dust_heavy");
                this.self.playVoiceSound(1);
                this.self.playSound("ssf2_snd_sfx_kirby_nspec_spit");
                this.self.inhale.spitFoe();
            };
        }

        internal function frame85():*
        {
            this.self.endAttack();
        }

        internal function frame86():*
        {
            this.fjmp_spit2 = currentFrame;
        }

        internal function frame88():*
        {
            this.self.playVoiceSound(1);
            this.self.inhale.spitFoe();
            this.self.attachEffect("global_dust_heavy");
            this.self.playSound("ssf2_snd_sfx_kirby_nspec_spit");
        }

        internal function frame102():*
        {
            this.self.endAttack();
        }

        internal function frame103():*
        {
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("inhale_fall_grabbed");
            };
        }

        internal function frame108():*
        {
            if (this.self.isOnGround())
            {
                this.self.inhale.setState(InhaleState.IDLE);
            }
            else
            {
                this.self.inhale.setState(InhaleState.FALL);
            };
        }

        internal function frame109():*
        {
        }

        internal function frame131():*
        {
            this.self.stancePlayFrame("inhale_hold_idle");
        }

        internal function frame132():*
        {
            this.self.flip();
        }

        internal function frame140():*
        {
            this.self.inhale.setState(InhaleState.IDLE);
        }

        internal function frame147():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step01");
            };
            SSF2API.getCamera().shake(3);
        }

        internal function frame156():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step02");
            };
            SSF2API.getCamera().shake(3);
        }

        internal function frame164():*
        {
            this.self.stancePlayFrame("inhale_hold_walk");
        }

        internal function frame165():*
        {
            this.self.updateAttackStats({"allowTurn":false});
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame170():*
        {
            this.self.setXSpeed(0);
            this.self.updateAttackStats({"xSpeedCap":5});
            this.self.setYSpeed(-8);
            this.self.updateAttackStats({"allowControl":true});
            this.self.inhale.setState(InhaleState.JUMP);
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
            SSF2API.getCamera().shake(3);
        }

        internal function frame185():*
        {
            this.self.inhale.setState(InhaleState.FALL);
        }

        internal function frame186():*
        {
            this.self.updateAttackStats({"allowTurn":false});
        }

        internal function frame191():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            this.self.setHurtInterrupt(null);
            this.self.setIntangibility(false);
            if (this.self.isOnGround())
            {
                this.self.inhale.setState(InhaleState.IDLE);
            }
            else
            {
                this.self.inhale.setState(InhaleState.FALL);
            };
        }

        internal function frame192():*
        {
            this.self.updateAttackStats({"xSpeedCap":5});
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame196():*
        {
            this.self.stancePlayFrame("inhale_hold_fall");
        }

        internal function frame197():*
        {
            SSF2API.getCamera().shake(10);
            this.self.updateAttackStats({
                "xSpeedCap":0,
                "allowTurn":false
            });
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("kirby_land2");
            };
        }

        internal function frame210():*
        {
            this.self.inhale.setState(InhaleState.IDLE);
        }

        internal function frame211():*
        {
            SSF2API.stopSound(this.sfxStop);
            SSF2API.stopSound(this.sfxStop2);
            this.self.playSound("dedede_inhale_end");
        }

        internal function frame218():*
        {
            this.self.refreshAttackID();
        }

        internal function frame219():*
        {
            this.self.updateAttackStats({"invincible":true});
            this.self.swallow();
        }

        internal function frame230():*
        {
            this.self.updateAttackStats({"invincible":false});
            this.self.endAttack();
        }

        internal function frame231():*
        {
            this.self.setIntangibility(true);
            this.self.setHurtInterrupt(this.onHurtInterrupt);
            if (this.proj.getType() === "SSF2Projectile")
            {
                if (this.proj && !(this.proj.isDisposed()))
                {
                    this.self.setGlobalVariable("dddGlobal", this.proj.exportStats());
                    this.projLinkage = this.proj.getProjectileStat("linkage_id");
                    if (this.projLinkage == "sora_strikeraidproj")
                    {
                        this.proj.destroy();
                        this.self.setGlobalVariable("dddGlobal", null);
                    }
                    else
                    {
                        switch (this.projLinkage)
                        {
                        case "bmmeteorprojectile":
                        this.self.setGlobalVariable("DDDProjMetadata", {"dmg":this.proj.getAttackBoxStat(1, "damage")});
                        break;
                        case "bacon":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "pal":this.proj.getPaletteSwapData(),
                            "pri":this.proj.getAttackBoxStat(1, "priority"),
                            "currentBacon":this.proj.getStanceMC().food.currentFrame
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
                        this.self.setGlobalVariable("DDDProjMetadata", {
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
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                        });
                        break;
                        case "link_arrow":
                        case "bombArrow":
                        this.self.setGlobalVariable("DDDProjMetadata", {
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
                        this.self.setGlobalVariable("DDDProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                        break;
                        case "aura_sphere":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant"),
                            "spd":this.proj.getProjectileStat("xspeed")
                        });
                        break;
                        case "hardknuckle":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "pal":this.proj.getPaletteSwapData()
                        });
                        break;
                        case "naruto_rasenganexplosionground":
                        this.self.setGlobalVariable("DDDProjMetadata", {"dmg":this.proj.getAttackBoxStat(2, "damage")});
                        break;
                        case "pichuthunderJolt2":
                        this.self.setGlobalVariable("DDDProjMetadata", {"prl":this.proj.getAttackBoxStat(1, "paralysis")});
                        break;
                        case "pit_arrow2":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "pal":this.proj.getStanceMC().altTrail
                        });
                        break;
                        case "hadoken":
                        case "command_hadoken":
                        case "shakunetsu_hadoken":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "spd":this.proj.getProjectileStat("xspeed"),
                            "tmx":this.proj.getProjectileStat("time_max")
                        });
                        break;
                        case "samus_chargeshot":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                        });
                        break;
                        case "zamus_pshot_weak":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "prl":this.proj.getAttackBoxStat(1, "paralysis")
                        });
                        break;
                        case 30:
                        default:
                        break;
                        }
                        this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
                    };
                };
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                if (this.proj && !(this.proj.isDisposed()))
                {
                    this.projLinkage = this.proj.getItemStat("linkage_id");
                    SSF2API.print(this.projLinkage);
                    this.proj.destroy();
                    switch (_local_1)
                    {
                    case "link_bomb":
                    this.self.setGlobalVariable("DDDProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                    break;
                    case 1:
                    default:
                    break;
                    }
                    this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
                    this.self.setGlobalVariable("dddGlobal", {
                        "nme":this.projLinkage,
                        "chr":this.charItemIdentifier()
                    });
                };
            };
        }

        internal function frame234():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.dispose();
                this.proj.destroy();
            };
        }

        internal function frame241():*
        {
            this.self.setHurtInterrupt(null);
            this.self.setIntangibility(false);
            if (!this.self.getGlobalVariable("dddGlobal"))
            {
                return;
            }
            else
            if (this.proj.getType() === "SSF2Projectile")
            {
                this.proj = this.self.fireProjectile(this.self.getGlobalVariable("dddGlobal"), 29, -10);
                this.projLinkage = this.proj.getProjectileStat("linkage_id");
                if (this.canSuspend())
                {
                    this.proj.stancePlayFrame("suspend");
                };
                if (this.isOwnGordo)
                {
                    this.self.gordo = this.proj;
                };
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                this.projLinkage = this.self.getGlobalVariable("dddGlobal").nme;
                this.itemChar = this.self.getGlobalVariable("dddGlobal").chr;
                if (this.itemChar != null)
                {
                    this.proj = this.self.generateCharacterItem(this.projLinkage, this.itemChar, true);
                }
                else
                {
                    this.proj = this.self.generateItem(this.projLinkage, true, false, true);
                };
                this.self.tossItem(12);
            };
            if (!(this.proj) || this.proj.isDisposed())
            {
                SSF2API.print("Projectile throw unsuccessful.");
                this.self.setGlobalVariable("dddGlobal", null);
                this.self.setGlobalVariable("DDDProjMetadata", null);
                return;
            };
            this.xScale = this.self.getGlobalVariable("xScale");
            this.yScale = this.self.getGlobalVariable("yScale");
            if ((this.self.isFacingRight() && (this.xScale < 0)) || (!(this.self.isFacingRight()) && (this.xScale > 0)))
            {
                this.xScale *= -1;
            };
            this.proj.setScale((this.xScale / this.self.getScale().x), (this.yScale / this.self.getScale().y));
            this.metadata = this.self.getGlobalVariable("DDDProjMetadata");
            if (this.proj.getType() === "SSF2Projectile")
            {
                if (this.metadata != null)
                {
                    switch (this.self.getGlobalVariable("dddGlobal").linkage_id)
                    {
                    case "bmmeteorprojectile":
                    this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                    break;
                    case "bacon":
                    this.proj.setPaletteSwapData(this.metadata.pal);
                    this.proj.updateAttackBoxStats(1, {"priority":this.metadata.pri});
                    this.proj.getStanceMC().food.gotoAndStop(this.metadata.currentBacon);
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
            }
            else if ((this.proj.getType() === "SSF2Item") && (this.metadata != null))
            {
                switch (_local_1)
                {
                case "link_bomb":
                this.proj.setPaletteSwapData(this.metadata.pal);
                break;
                case 1:
                default:
                break;
                }
            };
            SSF2API.print("Successfully threw projectile back.");
            this.self.setGlobalVariable("dddGlobal", null);
            this.self.setGlobalVariable("DDDProjMetadata", null);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-30
            });
        }

        internal function frame242():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            if (this.proj.getType() === "SSF2Item")
            {
                return;
            }
            else
            if (this.proj && !(this.proj.isDisposed()) && (this.proj.getType() === "SSF2Projectile"))
            {
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
                this.proj.updateProjectileStats({
                    "rotate":false,
                    "time_max":90
                });
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
        }

        internal function frame254():*
        {
            this.self.endAttack();
        }

        internal function frame255():*
        {
            this.self.setIntangibility(true);
            this.self.setHurtInterrupt(this.onHurtInterrupt);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGroundItemAnim);
            if (this.self.isOnGround())
            {
                this.toGroundItemAnim(null);
            };
            if (this.proj.getType() === "SSF2Projectile")
            {
                if (this.proj && !(this.proj.isDisposed()))
                {
                    this.self.setGlobalVariable("dddGlobal", this.proj.exportStats());
                    this.projLinkage = this.proj.getProjectileStat("linkage_id");
                    if (this.projLinkage == "sora_strikeraidproj")
                    {
                        this.proj.destroy();
                    }
                    else
                    {
                        switch (this.projLinkage)
                        {
                        case "bmmeteorprojectile":
                        this.self.setGlobalVariable("DDDProjMetadata", {"dmg":this.proj.getAttackBoxStat(1, "damage")});
                        break;
                        case "bacon":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "pal":this.proj.getPaletteSwapData(),
                            "pri":this.proj.getAttackBoxStat(1, "priority"),
                            "currentBacon":this.proj.getStanceMC().food.currentFrame
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
                        this.self.setGlobalVariable("DDDProjMetadata", {
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
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                        });
                        break;
                        case "link_arrow":
                        case "bombArrow":
                        this.self.setGlobalVariable("DDDProjMetadata", {
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
                        this.self.setGlobalVariable("DDDProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                        break;
                        case "aura_sphere":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant"),
                            "spd":this.proj.getProjectileStat("xspeed")
                        });
                        break;
                        case "hardknuckle":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "pal":this.proj.getPaletteSwapData()
                        });
                        break;
                        case "naruto_rasenganexplosionground":
                        this.self.setGlobalVariable("DDDProjMetadata", {"dmg":this.proj.getAttackBoxStat(2, "damage")});
                        break;
                        case "pichuthunderJolt2":
                        this.self.setGlobalVariable("DDDProjMetadata", {"prl":this.proj.getAttackBoxStat(1, "paralysis")});
                        break;
                        case "pit_arrow2":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "pal":this.proj.getStanceMC().altTrail
                        });
                        break;
                        case "hadoken":
                        case "command_hadoken":
                        case "shakunetsu_hadoken":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "spd":this.proj.getProjectileStat("xspeed"),
                            "tmx":this.proj.getProjectileStat("time_max")
                        });
                        break;
                        case "samus_chargeshot":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "bkb":this.proj.getAttackBoxStat(1, "power"),
                            "kbg":this.proj.getAttackBoxStat(1, "kbConstant")
                        });
                        break;
                        case "zamus_pshot_weak":
                        this.self.setGlobalVariable("DDDProjMetadata", {
                            "dmg":this.proj.getAttackBoxStat(1, "damage"),
                            "prl":this.proj.getAttackBoxStat(1, "paralysis")
                        });
                        break;
                        case 30:
                        default:
                        break;
                        }
                        this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
                    };
                };
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                if (this.proj && !(this.proj.isDisposed()))
                {
                    this.projLinkage = this.proj.getItemStat("linkage_id");
                    switch (_local_1)
                    {
                    case "link_bomb":
                    this.self.setGlobalVariable("DDDProjMetadata", {"pal":this.proj.getPaletteSwapData()});
                    break;
                    case 1:
                    default:
                    break;
                    }
                    this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
                    this.self.setGlobalVariable("dddGlobal", {
                        "nme":this.projLinkage,
                        "chr":this.charItemIdentifier()
                    });
                };
            };
        }

        internal function frame258():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.dispose();
                this.proj.destroy();
            };
        }

        internal function frame265():*
        {
            this.self.setHurtInterrupt(null);
            this.self.setIntangibility(false);
            if (!this.self.getGlobalVariable("dddGlobal"))
            {
                return;
            }
            else
            if (this.proj.getType() === "SSF2Projectile")
            {
                this.proj = this.self.fireProjectile(this.self.getGlobalVariable("dddGlobal"), 29, -10);
                this.projLinkage = this.proj.getProjectileStat("linkage_id");
                if (this.canSuspend())
                {
                    this.proj.stancePlayFrame("suspend");
                };
                if (this.isOwnGordo)
                {
                    this.self.gordo = this.proj;
                };
            }
            else if (this.proj.getType() === "SSF2Item")
            {
                this.projLinkage = this.self.getGlobalVariable("dddGlobal").nme;
                this.itemChar = this.self.getGlobalVariable("dddGlobal").chr;
                if (this.itemChar != null)
                {
                    this.proj = this.self.generateCharacterItem(this.projLinkage, this.itemChar, true);
                }
                else
                {
                    this.proj = this.self.generateItem(this.projLinkage, true, false, true);
                };
                this.self.tossItem(12);
            };
            if (!(this.proj) || this.proj.isDisposed())
            {
                SSF2API.print("Projectile throw unsuccessful.");
                this.self.setGlobalVariable("dddGlobal", null);
                this.self.setGlobalVariable("DDDProjMetadata", null);
                return;
            };
            this.xScale = this.self.getGlobalVariable("xScale");
            this.yScale = this.self.getGlobalVariable("yScale");
            if ((this.self.isFacingRight() && (this.xScale < 0)) || (!(this.self.isFacingRight()) && (this.xScale > 0)))
            {
                this.xScale *= -1;
            };
            this.proj.setScale((this.xScale / this.self.getScale().x), (this.yScale / this.self.getScale().y));
            this.metadata = this.self.getGlobalVariable("DDDProjMetadata");
            if (this.proj.getType() === "SSF2Projectile")
            {
                if (this.metadata != null)
                {
                    switch (this.self.getGlobalVariable("dddGlobal").linkage_id)
                    {
                    case "bmmeteorprojectile":
                    this.proj.updateAttackBoxStats(1, {"damage":this.metadata.dmg});
                    break;
                    case "bacon":
                    this.proj.setPaletteSwapData(this.metadata.pal);
                    this.proj.updateAttackBoxStats(1, {"priority":this.metadata.pri});
                    this.proj.getStanceMC().food.gotoAndStop(this.metadata.currentBacon);
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
            }
            else if ((this.proj.getType() === "SSF2Item") && (this.metadata != null))
            {
                switch (_local_1)
                {
                case "link_bomb":
                this.proj.setPaletteSwapData(this.metadata.pal);
                break;
                case 1:
                default:
                break;
                }
            };
            SSF2API.print("Successfully threw projectile back.");
            this.self.setGlobalVariable("dddGlobal", null);
            this.self.setGlobalVariable("DDDProjMetadata", null);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.onDestroy, {"persistent":true});
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-30
            });
        }

        internal function frame266():*
        {
            if (this.proj)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.onDestroy);
            };
            if (this.proj.getType() === "SSF2Item")
            {
                return;
            }
            else
            if (this.proj && !(this.proj.isDisposed()) && (this.proj.getType() === "SSF2Projectile"))
            {
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
        }

        internal function frame278():*
        {
            this.self.endAttack();
        }


    }
}


package dedede_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class DownSpecialGround_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var camBox:MovieClip;
        public var hammer1:MovieClip;
        public var hammer2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public const ANIM_IDLE:String = "ANIM_IDLE";
        public const ANIM_IMAX:String = "ANIM_IMAX";
        public const ANIM_WALK:String = "ANIM_WALK";
        public const ANIM_TURN:String = "ANIM_TURN";
        public const ANIM_JUMP:String = "ANIM_JUMP";
        public const ANIM_FALL:String = "ANIM_FALL";
        public const ANIM_LAND:String = "ANIM_LAND";
        public const DAMAGE_MIN:int = 12;
        public const DAMAGE_MAX:int = 40;
        public const DAMAGE_MIN_AIR:int = 11;
        public const DAMAGE_MAX_AIR:int = 32;
        public const CHARGE_MAX:int = 60;
        public var airFrames:*;
        public var anim:*;
        public var calculatedDamage:*;
        public var canFall:*;
        public var canJump:*;
        public var charge:*;
        public var controls:*;
        public var isLanding:*;
        public var isMax:*;
        public var isTurning:*;
        public var releaseLevel:*;
        public var sfxChargeStart:*;
        public var sfxChargeHold:*;
        public var curFrame:int;
        public var xSpeedAir:int;
        public var xSpeedGround:int;
        public var fjmp_start1:int;
        public var fjmp_start2:int;

        public function DownSpecialGround_58()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 9, this.frame10, 13, this.frame14, 18, this.frame19, 23, this.frame24, 27, this.frame28, 28, this.frame29, 33, this.frame34, 34, this.frame35, 38, this.frame39, 43, this.frame44, 48, this.frame49, 53, this.frame54, 56, this.frame57, 57, this.frame58, 60, this.frame61, 61, this.frame62, 67, this.frame68, 68, this.frame69, 73, this.frame74, 80, this.frame81, 81, this.frame82, 86, this.frame87, 88, this.frame89, 91, this.frame92, 96, this.frame97, 97, this.frame98, 101, this.frame102, 106, this.frame107, 111, this.frame112, 116, this.frame117, 121, this.frame122, 126, this.frame127, 128, this.frame129, 133, this.frame134, 134, this.frame135, 138, this.frame139, 139, this.frame140, 162, this.frame163, 163, this.frame164, 166, this.frame167, 167, this.frame168, 195, this.frame196, 197, this.frame198, 203, this.frame204);
        }

        public function toGroundStart(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundStart);
            this.airFrames = false;
            this.curFrame = (currentFrame - (this.fjmp_start2 - this.fjmp_start1));
            SSF2API.print(this.curFrame.toString());
            this.self.stancePlayFrame(this.curFrame);
        }

        public function updateStatus():void
        {
            this.checkPresses();
            this.animator();
            if (!this.self.getControls().BUTTON1)
            {
                this.self.destroyTimer(this.updateStatus);
            };
        }

        public function checkPresses():void
        {
            var _local_1:Boolean;
            this.controls = this.self.getControls();
            if (this.self.isOnGround())
            {
                if (!(this.canJump) && !(this.controls.JUMP))
                {
                    this.canJump = true;
                };
                if (!(this.canFall) && !(this.controls.DOWN))
                {
                    this.canFall = true;
                };
            }
            else if (this.controls.DOWN)
            {
                this.canFall = true;
            };
            if (!this.controls.BUTTON1)
            {
                if (this.charge > this.CHARGE_MAX)
                {
                    this.releaseLevel = 2;
                }
                else
                {
                    this.releaseLevel = 1;
                };
                this.self.updateAttackStats({
                    "forceFallThrough":false,
                    "allowJump":false,
                    "allowRun":false,
                    "allowTurn":false
                });
            }
            else
            {
                _local_1 = this.self.getAttackStat("forceFallThrough");
                if (!(this.controls.DOWN && this.canFall == _local_1))
                {
                    this.self.updateAttackStats({"forceFallThrough":!(_local_1)});
                };
                if (this.charge >= this.CHARGE_MAX)
                {
                    if (this.charge == this.CHARGE_MAX)
                    {
                        this.isMax = true;
                        if (this.hammer1 && this.hammer2)
                        {
                            this.hammer2.visible = this.hammer1.visible;
                            this.hammer1.visible = false;
                        };
                    }
                    else if ((this.charge % 15) == 0)
                    {
                        this.hurtSelf();
                    };
                };
                this.charge++;
            };
        }

        public function animator():void
        {
            this.controls = this.self.getControls();
            if (this.releaseLevel > 0)
            {
                if (this.releaseLevel == 1)
                {
                    this.self.stancePlayFrame("weak_swing");
                }
                else
                {
                    this.self.stancePlayFrame("full_swing");
                };
                return;
            }
            else
            if (!this.self.isOnGround())
            {
                if (!this.airFrames)
                {
                    this.self.stancePlayFrame("falling");
                    this.anim = this.ANIM_FALL;
                    this.airFrames = true;
                    this.canJump = false;
                };
            }
            else if (!this.airFrames)
            {
                if (this.anim == this.ANIM_LAND)
                {
                    return;
                }
            else
                if (this.controls.JUMP && this.canJump && (this.anim != this.ANIM_JUMP))
                {
                    this.self.stancePlayFrame("jumping");
                    this.anim = this.ANIM_JUMP;
                    this.airFrames = true;
                    this.canJump = false;
                }
                else if ((this.controls.LEFT != this.controls.RIGHT) && (this.anim != this.ANIM_TURN))
                {
                    if (this.self.isFacingRight() == this.controls.LEFT)
                    {
                        this.self.stancePlayFrame("turning");
                        this.anim = this.ANIM_TURN;
                        return;
                    }
            else
                    if (this.anim != this.ANIM_WALK)
                    {
                        if (this.isMax)
                        {
                            this.self.stancePlayFrame("standingMaxEnd");
                        }
                        else
                        {
                            this.self.stancePlayFrame("moving");
                        };
                        this.anim = this.ANIM_WALK;
                    };
                }
                else if (this.isMax && (this.controls.LEFT == this.controls.RIGHT) && (this.anim != this.ANIM_IMAX) && (this.anim != this.ANIM_TURN))
                {
                    this.self.stancePlayFrame("standingMax");
                    this.anim = this.ANIM_IMAX;
                }
                else if ((this.controls.LEFT == this.controls.RIGHT) && (this.anim != this.ANIM_IDLE) && (this.anim != this.ANIM_IMAX) && (this.anim != this.ANIM_TURN))
                {
                    this.self.stancePlayFrame("standing");
                    this.anim = this.ANIM_IDLE;
                };
            }
            else if ((this.anim != this.ANIM_LAND) && (this.anim != this.ANIM_JUMP))
            {
                this.self.stancePlayFrame("landing");
                this.anim = this.ANIM_LAND;
                this.airFrames = false;
            };
        }

        public function hurtSelf():void
        {
            if (this.self.getCharacterStat("stamina") <= 0)
            {
                this.self.setDamage((this.self.getDamage() + 1));
            }
            else
            {
                this.self.setDamage((this.self.getDamage() - 1));
            };
            this.self.throbDamageCounter();
        }

        public function delayAudioLoop():void
        {
            this.chargeHoldAudio();
            this.self.createTimer(11, -1, this.chargeHoldAudio);
        }

        public function chargeHoldAudio():void
        {
            SSF2API.stopSound(this.sfxChargeHold);
            this.sfxChargeHold = SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_loop");
        }

        public function stopAudio(_arg_1:Event=null):void
        {
            SSF2API.stopSound(this.sfxChargeStart);
            SSF2API.stopSound(this.sfxChargeHold);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.anim = this.ANIM_IDLE;
            this.canFall = false;
            this.canJump = true;
            this.charge = 0;
            this.controls = null;
            this.isLanding = false;
            this.isMax = false;
            this.isTurning = false;
            this.releaseLevel = 0;
            this.curFrame = 0;
            if (SSF2API.isReady() && this.self && (this.curFrame != currentFrame))
            {
                this.xSpeedAir = this.self.getCharacterStat("max_xSpeed");
                this.xSpeedGround = this.self.getCharacterStat("norm_xSpeed");
                this.airFrames = (!(this.self.isOnGround()));
                this.fjmp_start1 = currentFrame;
                if (!this.self.isOnGround())
                {
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGroundStart);
                    this.self.stancePlayFrame("airStart");
                };
            };
        }

        internal function frame4():*
        {
            if (this.curFrame != currentFrame)
            {
                SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_start");
            };
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("standing");
            this.self.createTimer(1, -1, this.updateStatus);
            this.self.updateAttackStats({"allowRun":true});
            this.sfxChargeStart = SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_charge");
            this.self.createTimer(149, 1, this.delayAudioLoop);
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.stopAudio);
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.stopAudio);
        }

        internal function frame10():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":this.xSpeedGround,
                "allowTurn":true
            });
            this.self.attachEffect("global_dust_heavy");
            this.hammer1.visible = (this.charge <= this.CHARGE_MAX);
            this.hammer2.visible = (this.charge > this.CHARGE_MAX);
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame19():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame24():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame28():*
        {
            this.self.stancePlayFrame("standing");
        }

        internal function frame29():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":this.xSpeedGround,
                "allowTurn":true
            });
            this.self.attachEffect("global_dust_heavy");
            this.hammer1.visible = (this.charge <= this.CHARGE_MAX);
            this.hammer2.visible = (this.charge > this.CHARGE_MAX);
        }

        internal function frame34():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame35():*
        {
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
        }

        internal function frame39():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame44():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame49():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame54():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame57():*
        {
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
        }

        internal function frame58():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame61():*
        {
            this.self.stancePlayFrame("moving");
        }

        internal function frame62():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":5,
                "allowTurn":false
            });
            this.hammer1.visible = (this.charge <= this.CHARGE_MAX);
            this.hammer2.visible = (this.charge > this.CHARGE_MAX);
        }

        internal function frame68():*
        {
            this.self.stancePlayFrame("falling");
        }

        internal function frame69():*
        {
            this.self.updateAttackStats({"allowTurn":false});
            this.hammer1.visible = (this.charge <= this.CHARGE_MAX);
            this.hammer2.visible = (this.charge > this.CHARGE_MAX);
        }

        internal function frame74():*
        {
            this.self.updateAttackStats({"xSpeedCap":4});
            this.self.setYSpeed(-17);
            SSF2API.playSound("ssf2_snd_sfx_dedede_jump01");
        }

        internal function frame81():*
        {
            this.self.stancePlayFrame("falling");
            this.anim = this.ANIM_FALL;
        }

        internal function frame82():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":0,
                "allowTurn":false
            });
            SSF2API.playSound("ssf2_snd_sfx_dedede_landHeavy");
            this.hammer1.visible = (this.charge <= this.CHARGE_MAX);
            this.hammer2.visible = (this.charge > this.CHARGE_MAX);
        }

        internal function frame87():*
        {
            this.self.stancePlayFrame("standing");
            this.anim = this.ANIM_IDLE;
        }

        internal function frame89():*
        {
            this.fjmp_start2 = currentFrame;
            this.self.updateAttackStats({
                "xSpeedCap":this.xSpeedAir,
                "allowTurn":false
            });
        }

        internal function frame92():*
        {
            SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_start");
        }

        internal function frame97():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundStart);
            this.self.createTimer(1, -1, this.updateStatus);
            this.self.updateAttackStats({"allowRun":true});
            this.sfxChargeStart = SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_charge");
            this.self.createTimer(149, 1, this.delayAudioLoop);
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.stopAudio);
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.stopAudio);
            this.self.stancePlayFrame("falling");
        }

        internal function frame98():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":this.xSpeedGround,
                "allowTurn":true
            });
        }

        internal function frame102():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame107():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame112():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame117():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame122():*
        {
            this.self.stancePlayFrame("standingMaxLoop");
        }

        internal function frame127():*
        {
            this.self.stancePlayFrame("moving");
        }

        internal function frame129():*
        {
            this.self.updateAttackStats({
                "xSpeedCap":this.xSpeedGround,
                "allowTurn":true
            });
        }

        internal function frame134():*
        {
            this.self.stancePlayFrame("moving");
            this.anim = this.ANIM_WALK;
        }

        internal function frame135():*
        {
            SSF2API.stopSound(this.sfxChargeStart);
            SSF2API.stopSound(this.sfxChargeHold);
            this.self.destroyTimer(this.delayAudioLoop);
            this.self.destroyTimer(this.chargeHoldAudio);
        }

        internal function frame139():*
        {
            if (this.self.isOnGround())
            {
                this.calculatedDamage = (this.DAMAGE_MIN + ((this.DAMAGE_MAX - this.DAMAGE_MIN) * (this.charge / this.CHARGE_MAX)));
            }
            else
            {
                this.calculatedDamage = (this.DAMAGE_MIN_AIR + ((this.DAMAGE_MAX_AIR - this.DAMAGE_MIN_AIR) * (this.charge / this.CHARGE_MAX)));
            };
            this.self.updateAttackBoxStats(1, {"damage":this.calculatedDamage});
            this.self.updateAttackBoxStats(2, {"damage":this.calculatedDamage});
        }

        internal function frame140():*
        {
            SSF2API.getCamera().shake(5);
            SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_weak");
        }

        internal function frame163():*
        {
            this.self.endAttack();
        }

        internal function frame164():*
        {
            SSF2API.stopSound(this.sfxChargeStart);
            SSF2API.stopSound(this.sfxChargeHold);
            this.self.destroyTimer(this.delayAudioLoop);
            this.self.destroyTimer(this.chargeHoldAudio);
            this.self.updateAttackStats({"canFallOff":false});
        }

        internal function frame167():*
        {
            this.calculatedDamage = ((this.self.isOnGround()) ? this.DAMAGE_MAX : this.DAMAGE_MAX_AIR);
            this.self.updateAttackBoxStats(1, {
                "damage":this.calculatedDamage,
                "hitStun":8,
                "selfHitStun":8
            });
            this.self.updateAttackBoxStats(2, {
                "damage":this.calculatedDamage,
                "hitStun":8,
                "selfHitStun":8
            });
        }

        internal function frame168():*
        {
            SSF2API.getCamera().shake(10);
            SSF2API.playSound("ssf2_snd_sfx_dedede_dspec_strong");
            this.self.setXSpeed(10, false);
        }

        internal function frame196():*
        {
            if (this.self.isOnGround())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_l1");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_step01");
                };
            };
        }

        internal function frame198():*
        {
            if (this.self.isOnGround())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_l2");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_step02");
                };
            };
        }

        internal function frame204():*
        {
            this.self.endAttack();
        }


    }
}


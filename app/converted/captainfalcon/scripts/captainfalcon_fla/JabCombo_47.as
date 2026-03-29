package captainfalcon_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class JabCombo_47 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var looped:Boolean;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public var rapid:Boolean;
        public var playsound:Number;
        public var audio:Number;
        public var controls:Object;
        public var used:Boolean;
        public var used2:Boolean;
        public var time:Number;
        public var rand:int;
        public var jabFinishStats:Object;

        public function JabCombo_47()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 5, this.frame6, 6, this.frame7, 7, this.frame8, 10, this.frame11, 14, this.frame15, 15, this.frame16, 16, this.frame17, 18, this.frame19, 19, this.frame20, 24, this.frame25, 25, this.frame26, 26, this.frame27, 27, this.frame28, 28, this.frame29, 29, this.frame30, 30, this.frame31, 31, this.frame32, 32, this.frame33, 33, this.frame34, 34, this.frame35, 35, this.frame36, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 41, this.frame42, 42, this.frame43, 63, this.frame64);
        }

        public function checkControls():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON2)
            {
                this.pressed1 = true;
            };
            if (this.pressed1 && this.controls.BUTTON2)
            {
                this.pressed2 = true;
            };
        }

        public function checkForGoToJab2():*
        {
            if (this.pressed2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("hit2");
            };
        }

        public function checkForGoToJab3():*
        {
            if (this.pressed2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("hit3");
            };
        }

        public function checkForGoToJab4():*
        {
            if (this.pressed2 && !(this.rapid))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.rapid = true;
                this.self.destroyTimer(this.checkControls);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.looped = false;
            this.pressed1 = false;
            this.pressed2 = false;
            this.rapid = false;
            if (SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame2():*
        {
            this.controls = this.self.getControls();
            this.used = this.self.getGlobalVariable("jab");
            this.used2 = this.self.getGlobalVariable("jab2");
            this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            if (this.used && (this.time <= 12))
            {
                this.self.stancePlayFrame("hit2");
            }
            else if (this.used2 && (this.time <= 12))
            {
                this.self.stancePlayFrame("hit3");
            }
            else
            {
                this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_jab1", {
                    "scaleX":1.15,
                    "scaleY":1.15,
                    "parentLock":true,
                    "syncHitStun":true
                }));
                this.self.clearEffectsOnStateChange(false);
                this.self.setGlobalVariable("jab", true);
                this.self.setGlobalVariable("jab2", false);
            };
            this.pressed1 = false;
            this.self.createTimer(1, 4, this.checkControls);
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(52),
                "y":-42,
                "parentLock":true
            });
            this.self.playAttackSound(1);
        }

        internal function frame4():*
        {
            this.self.createTimer(1, 2, this.checkForGoToJab2);
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {"damage":3});
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", true);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.removeAllEffects();
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(65),
                "y":-45,
                "parentLock":true
            });
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.pressed1 = false;
            this.self.createTimer(1, 7, this.checkControls);
            this.self.createTimer(1, 3, this.checkForGoToJab4);
            this.self.playAttackSound(2);
        }

        internal function frame11():*
        {
            this.self.destroyTimer(this.checkForGoToJab4);
            if (!this.rapid)
            {
                this.self.createTimer(1, 4, this.checkForGoToJab3);
            }
            else
            {
                this.self.setXSpeed(6, false);
                this.self.stancePlayFrame("hit4");
            };
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }

        internal function frame16():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "power":85,
                "kbConstant":40,
                "direction":60,
                "effectSound":"brawl_punch_l"
            });
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.removeAllEffects();
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab3);
        }

        internal function frame17():*
        {
            this.self.setXSpeed(9, false);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.pressed1 = false;
            this.self.createTimer(1, 5, this.checkControls);
            this.self.playAttackSound(3);
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame19():*
        {
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":0.5,
                "power":0,
                "kbConstant":50,
                "direction":35,
                "hitStun":1,
                "selfHitStun":0,
                "effectSound":"brawl_punch_s",
                "stackKnockback":false
            });
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab4);
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON2)
            {
                this.self.endAttack();
            }
            else
            {
                this.pressed1 = false;
                this.self.createTimer(1, -1, this.checkControls);
            };
        }

        internal function frame27():*
        {
            this.self.refreshAttackID();
            this.self.playSound("cfalcon_jabcombo1");
        }

        internal function frame28():*
        {
            this.self.removeAllEffects();
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(55),
                "y":-60
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame29():*
        {
            if (this.pressed2 || this.controls.BUTTON2 || !(this.looped))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.looped = true;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame30():*
        {
            this.self.refreshAttackID();
            this.self.playSound("cfalcon_jabcombo2");
        }

        internal function frame31():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(63),
                "y":-50
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame32():*
        {
            if (this.pressed2 || this.controls.BUTTON2 || !(this.looped))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.looped = true;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame33():*
        {
            this.self.refreshAttackID();
            this.self.playSound("cfalcon_jabcombo3");
        }

        internal function frame34():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(58),
                "y":-40
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame35():*
        {
            if (this.pressed2 || this.controls.BUTTON2 || !(this.looped))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.looped = true;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame36():*
        {
            this.self.refreshAttackID();
            this.self.playSound("cfalcon_jabcombo3");
        }

        internal function frame37():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(63),
                "y":-50
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame38():*
        {
            if (this.pressed2 || this.controls.BUTTON2 || !(this.looped))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.looped = true;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame39():*
        {
            this.rand = 0;
            if (this.pressed2 || this.controls.BUTTON2 || !(this.looped))
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.looped = true;
                this.self.stancePlayFrame("again");
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 6)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
            this.jabFinishStats = {
                "selfHitStun":2,
                "hitStun":4,
                "damage":3,
                "direction":45,
                "power":55,
                "kbConstant":115,
                "effect_id":"effect_heavyHit",
                "effectSound":"brawl_punch_l",
                "stackKnockback":true
            };
            this.self.updateAttackBoxStats(1, this.jabFinishStats);
            this.self.updateAttackBoxStats(2, this.jabFinishStats);
            this.self.refreshAttackID();
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(18)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(18)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(18), 0);
            };
        }

        internal function frame42():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(15)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(15)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(15), 0);
            };
        }

        internal function frame43():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(32),
                "y":-48
            });
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.playSound("cfalcon_swing_ll");
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame64():*
        {
            this.self.endAttack();
        }


    }
}


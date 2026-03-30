package bandanadee_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class JabCombo_30 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;
        public var controls:Object;
        public var used:Boolean;
        public var used2:Boolean;
        public var time:Number;
        public var looped:Boolean;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public var rand:int;

        public function JabCombo_30()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 7, this.frame8, 9, this.frame10, 10, this.frame11, 13, this.frame14, 15, this.frame16, 16, this.frame17, 18, this.frame19, 19, this.frame20, 21, this.frame22, 22, this.frame23, 24, this.frame25, 25, this.frame26, 27, this.frame28, 28, this.frame29, 29, this.frame30, 30, this.frame31, 31, this.frame32, 33, this.frame34, 34, this.frame35, 35, this.frame36, 36, this.frame37, 50, this.frame51);
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

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.controls = this.self.getControls();
                this.used = this.self.getGlobalVariable("jab");
                this.used2 = this.self.getGlobalVariable("jab2");
                this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                this.looped = false;
                if (this.used && (this.time <= 12))
                {
                    this.self.stancePlayFrame("hit2");
                };
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame2():*
        {
            this.self.setGlobalVariable("jab", true);
            this.pressed1 = false;
            this.self.createTimer(1, 7, this.checkControls);
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame8():*
        {
            this.checkForGoToJab2();
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }

        internal function frame11():*
        {
            this.self.updateAttackStats({"refreshRate":2});
            this.self.updateAttackBoxStats(1, {
                "selfHitStun":0,
                "hitStun":2,
                "hitLag":-1.2,
                "damage":0.7,
                "direction":20,
                "power":5,
                "kbConstant":50,
                "effectSound":"sw_brawl_hit_S",
                "sdiDistance":0.7
            });
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
            this.pressed1 = false;
            this.self.createTimer(1, -1, this.checkControls);
        }

        internal function frame14():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame16():*
        {
            this.rand = 0;
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
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 4)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame17():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame19():*
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
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 4)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame20():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame22():*
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
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 4)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame23():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame25():*
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
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 4)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame26():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame28():*
        {
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
                if (this.rand >= 4)
                {
                    this.self.stancePlayFrame("finish");
                };
            };
        }

        internal function frame29():*
        {
            this.self.updateAttackStats({"refreshRate":3});
            this.self.updateAttackBoxStats(1, {
                "hitStun":2,
                "damage":1,
                "direction":75,
                "power":35,
                "kbConstant":0,
                "stackKnockback":true,
                "effectSound":"sw_brawl_hit_S",
                "effect_id":"effect_swordSlash",
                "sdiDistance":1,
                "reversableAngle":false
            });
            this.self.updateAttackBoxStats(2, {
                "hitStun":2,
                "damage":1,
                "direction":75,
                "power":35,
                "kbConstant":0,
                "stackKnockback":true,
                "effectSound":"sw_brawl_hit_S",
                "effect_id":"effect_swordSlash",
                "sdiDistance":1,
                "reversableAngle":false
            });
            this.self.updateAttackBoxStats(3, {
                "hitStun":2,
                "damage":1,
                "direction":75,
                "power":35,
                "kbConstant":0,
                "stackKnockback":true,
                "effectSound":"sw_brawl_hit_S",
                "effect_id":"effect_swordSlash",
                "sdiDistance":1,
                "reversableAngle":false
            });
            this.self.refreshAttackID();
            this.self.playSound("bandanadee_uspecSpin");
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(10), 0);
            };
        }

        internal function frame30():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(7.5)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(7.5)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(7.5), 0);
            };
        }

        internal function frame31():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(5)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(5)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(5), 0);
            };
        }

        internal function frame32():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(2.5)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(2.5)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(2.5), 0);
            };
        }

        internal function frame34():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(10), 0);
            };
            this.self.updateAttackStats({"refreshRate":10});
            this.self.updateAttackBoxStats(1, {
                "selfHitStun":1,
                "hitStun":3,
                "damage":3,
                "direction":35,
                "power":45,
                "kbConstant":120,
                "stackKnockback":true,
                "effectSound":"sw_brawl_hit_M",
                "effect_id":"effect_swordSlash",
                "sdiDistance":1
            });
            this.self.updateAttackBoxStats(2, {
                "selfHitStun":1,
                "hitStun":3,
                "damage":3,
                "direction":35,
                "power":45,
                "kbConstant":120,
                "stackKnockback":true,
                "effectSound":"sw_brawl_hit_M",
                "effect_id":"effect_swordSlash",
                "sdiDistance":1
            });
            this.self.refreshAttackID();
        }

        internal function frame35():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(5)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(5)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(5), 0);
            };
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
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

        internal function frame36():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(3)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(3)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(3), 0);
            };
            this.self.playAttackSound(2);
        }

        internal function frame37():*
        {
            SSF2API.getCamera().shake(5);
            this.self.playSound("brawl_kick_m");
            this.self.attachEffect("global_dust_heavy_rv", {
                "x":this.self.flipX(28),
                "scaleX":-0.7,
                "scaleY":-0.7
            });
        }

        internal function frame51():*
        {
            this.self.endAttack();
        }


    }
}


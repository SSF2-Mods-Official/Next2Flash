package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_jabcombo_26 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var time:Number;
        public var controls:Object;
        public var used:Boolean;
        public var used2:Boolean;
        public var pressed1:Boolean;
        public var pressed2:Boolean;

        public function bomberman_jabcombo_26()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 7, this.frame8, 8, this.frame9, 9, this.frame10, 11, this.frame12, 13, this.frame14, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 31, this.frame32, 33, this.frame34);
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

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                this.controls = this.self.getControls();
                this.used = this.self.getGlobalVariable("jab");
                this.used2 = this.self.getGlobalVariable("jab2");
                if (this.used && (this.time <= 12))
                {
                    this.self.stancePlayFrame("hit2");
                }
                else if (this.used2 && (this.time <= 10))
                {
                    this.self.stancePlayFrame("hit3");
                };
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(25),
                "y":-25,
                "parentLock":true
            });
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_jab1", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            this.self.playAttackSound(1);
        }

        internal function frame3():*
        {
            this.self.setGlobalVariable("jab", true);
            this.self.setGlobalVariable("jab2", false);
            this.pressed1 = false;
            this.self.createTimer(1, 5, this.checkControls);
        }

        internal function frame4():*
        {
            this.self.createTimer(1, 4, this.checkForGoToJab2);
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {"direction":80});
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", true);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
        }

        internal function frame10():*
        {
            this.pressed1 = false;
            this.self.createTimer(1, 9, this.checkControls);
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(38),
                "y":-22,
                "parentLock":true
            });
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_jab2", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.playAttackSound(2);
        }

        internal function frame14():*
        {
            this.self.createTimer(1, 5, this.checkForGoToJab3);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.self.updateAttackBoxStats(1, {
                "effectSound":"brawl_kick_m",
                "effect_id":"effect_hit1",
                "damage":5,
                "power":56,
                "kbConstant":60,
                "direction":35,
                "hitLag":-1
            });
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab3);
        }

        internal function frame21():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_jab", {
                "x":this.self.flipX(-28),
                "y":-52,
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame22():*
        {
            this.self.setXSpeed(6, false);
            this.self.attachEffect("global_dust_light");
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_jab3", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.playAttackSound(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame32():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}


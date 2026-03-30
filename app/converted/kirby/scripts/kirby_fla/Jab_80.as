package kirby_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class Jab_80 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var used:Boolean;
        public var used2:Boolean;
        public var time:Number;
        public var looped:Boolean;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public var jab2Stats:Object;
        public var rapidJabStats:Object;
        public var rand:int;
        public var jabFinishStats:Object;

        public function Jab_80()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 9, this.frame10, 10, this.frame11, 12, this.frame13, 14, this.frame15, 18, this.frame19, 19, this.frame20, 21, this.frame22, 22, this.frame23, 24, this.frame25, 25, this.frame26, 27, this.frame28, 28, this.frame29, 30, this.frame31, 31, this.frame32, 33, this.frame34, 34, this.frame35, 36, this.frame37, 55, this.frame56);
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.used = this.self.getGlobalVariable("jab");
                this.used2 = this.self.getGlobalVariable("jab2");
                this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                this.looped = false;
                if (this.time <= 11)
                {
                    if (this.used)
                    {
                        this.self.stancePlayFrame("hit2");
                    }
                    else if (this.used2)
                    {
                        this.self.stancePlayFrame("hit3");
                    };
                };
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(45),
                "y":-17,
                "parentLock":true
            });
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
            this.self.setGlobalVariable("jab", true);
            this.self.setGlobalVariable("jab2", false);
            this.self.createTimer(1, 7, this.checkControls);
            this.self.playAttackSound(1);
        }

        internal function frame4():*
        {
            this.self.createTimer(1, 6, this.checkForGoToJab2);
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }

        internal function frame11():*
        {
            this.jab2Stats = {
                "hitLag":-1,
                "selfHitStun":0,
                "hitStun":4,
                "damage":3,
                "direction":70,
                "power":10,
                "kbConstant":30,
                "stackKnockback":false
            };
            this.self.updateAttackBoxStats(1, this.jab2Stats);
            this.self.updateAttackBoxStats(2, this.jab2Stats);
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", true);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
            this.self.createTimer(1, 10, this.checkControls);
        }

        internal function frame13():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(50),
                "y":-19,
                "parentLock":true
            });
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.createTimer(1, 4, this.checkForGoToJab3);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.rapidJabStats = {
                "selfHitStun":0,
                "hitStun":1,
                "damage":0.5,
                "direction":70,
                "power":0,
                "kbConstant":85
            };
            this.self.updateAttackBoxStats(1, this.rapidJabStats);
            this.self.updateAttackBoxStats(2, this.rapidJabStats);
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(8)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(8)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(8), 0);
            };
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab3);
            this.self.createTimer(1, -1, this.checkControls);
            this.self.playVoiceSound(1);
        }

        internal function frame22():*
        {
            this.self.refreshAttackID();
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
            this.self.playAttackSound(2);
        }

        internal function frame25():*
        {
            this.self.refreshAttackID();
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

        internal function frame26():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
        }

        internal function frame28():*
        {
            this.self.refreshAttackID();
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

        internal function frame29():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
        }

        internal function frame31():*
        {
            this.self.refreshAttackID();
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

        internal function frame32():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-8)});
        }

        internal function frame34():*
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

        internal function frame35():*
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
                "stackKnockback":true,
                "reversableAngle":false
            };
            this.self.updateAttackBoxStats(1, this.jabFinishStats);
            this.self.updateAttackBoxStats(2, this.jabFinishStats);
            this.self.refreshAttackID();
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(11)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(11)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(11), 0);
            };
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(11)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(11)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(11), 0);
            };
        }

        internal function frame37():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(3),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.playSound("ssf2_snd_sfx_kirby_swing_m");
        }

        internal function frame56():*
        {
            this.self.endAttack();
        }


    }
}


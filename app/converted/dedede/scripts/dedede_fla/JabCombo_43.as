package dedede_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class JabCombo_43 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var release:Boolean;
        public var press:Boolean;
        public var cancel:String;
        public var repeats:Number;
        public var soundLoop:*;
        public var jab2Stats1:Object;
        public var jab2Stats2:Object;
        public var rapidJabStats1:Object;
        public var rapidJabStats2:Object;
        public var jabFinishStats:Object;

        public function JabCombo_43()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 12, this.frame13, 15, this.frame16, 16, this.frame17, 18, this.frame19, 24, this.frame25, 29, this.frame30, 31, this.frame32, 32, this.frame33, 35, this.frame36, 38, this.frame39, 41, this.frame42, 42, this.frame43, 44, this.frame45, 63, this.frame64);
        }

        public function checkInputs(_arg_1:*=null):*
        {
            if (this.release && this.self.getControls().BUTTON2)
            {
                this.press = true;
            };
            if (!(this.release) && !this.self.getControls().BUTTON2)
            {
                this.release = true;
            };
            if ((this.cancel != "") && this.press)
            {
                this.press = false;
                this.release = false;
                this.self.stancePlayFrame(this.cancel);
                this.cancel = "";
            };
        }

        public function delayRapidJabSound():*
        {
            this.loopRapidJabSound();
            this.self.createTimer(8, -1, this.loopRapidJabSound);
        }

        public function loopRapidJabSound(_arg_1:*=null):*
        {
            SSF2API.stopSound(this.soundLoop);
            if (!this.soundLoop)
            {
                this.soundLoop = this.self.playSound("ssf2_snd_sfx_dedede_rapidJab");
            }
            else
            {
                this.soundLoop = this.self.playSound("ssf2_snd_sfx_dedede_rapidJab_loop");
            };
        }

        public function stopRapidJabSound(_arg_1:*=null):*
        {
            this.self.destroyTimer(this.delayRapidJabSound);
            this.self.destroyTimer(this.loopRapidJabSound);
            SSF2API.stopSound(this.soundLoop);
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.stopRapidJabSound);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.release = false;
            this.press = false;
            this.cancel = "";
            this.repeats = 0;
            this.jab2Stats1 = {
                "hitLag":-1,
                "selfHitStun":0,
                "hitStun":4,
                "damage":3,
                "direction":20,
                "power":10,
                "kbConstant":30,
                "stackKnockback":false
            };
            this.jab2Stats2 = {
                "hitLag":-1,
                "selfHitStun":0,
                "hitStun":4,
                "damage":3,
                "direction":110,
                "power":25,
                "kbConstant":30,
                "stackKnockback":false
            };
            this.rapidJabStats1 = {
                "selfHitStun":0,
                "hitStun":2,
                "damage":1,
                "direction":20,
                "power":30,
                "kbConstant":60,
                "effectSound":"ssf2_snd_sfx_dedede_hit_s"
            };
            this.rapidJabStats2 = {
                "selfHitStun":0,
                "hitStun":2,
                "damage":1,
                "direction":20,
                "power":5,
                "kbConstant":60,
                "effectSound":"ssf2_snd_sfx_dedede_hit_s"
            };
            this.jabFinishStats = {
                "selfHitStun":2,
                "hitStun":4,
                "damage":4,
                "direction":40,
                "power":50,
                "kbConstant":115,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "stackKnockback":true
            };
            if (SSF2API.isReady() && this.self)
            {
                this.self.createTimer(1, -1, this.checkInputs);
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
        }

        internal function frame8():*
        {
            this.cancel = "jab2";
        }

        internal function frame13():*
        {
            this.cancel = "";
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.self.updateAttackBoxStats(1, this.jab2Stats1);
            this.self.updateAttackBoxStats(2, this.jab2Stats2);
            this.self.refreshAttackID();
        }

        internal function frame19():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame25():*
        {
            this.cancel = "jab3";
        }

        internal function frame30():*
        {
            this.cancel = "";
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame33():*
        {
            this.self.destroyTimer(this.checkInputs);
            this.self.updateAttackBoxStats(1, this.rapidJabStats1);
            this.self.updateAttackBoxStats(2, this.rapidJabStats2);
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(8)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(8)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(8), 0);
            };
        }

        internal function frame36():*
        {
            if (this.repeats == 0)
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.stopRapidJabSound);
                this.loopRapidJabSound();
                this.self.createTimer(15, 1, this.delayRapidJabSound);
                this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
            };
            this.self.refreshAttackID();
        }

        internal function frame39():*
        {
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame42():*
        {
            if (this.self.getControls().BUTTON2 || (this.repeats < 1))
            {
                this.repeats++;
                this.self.stancePlayFrame("loop");
            }
            else
            {
                this.stopRapidJabSound();
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame43():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            this.self.updateAttackBoxStats(1, this.jabFinishStats);
            this.self.updateAttackBoxStats(2, this.jabFinishStats);
            this.self.refreshAttackID();
        }

        internal function frame45():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(6)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(6), 0);
            };
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame64():*
        {
            this.self.endAttack();
        }


    }
}


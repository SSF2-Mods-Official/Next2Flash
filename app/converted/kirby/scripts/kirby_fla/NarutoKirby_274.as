package kirby_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class NarutoKirby_274 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var oodama:Boolean;
        public var hasHit:Boolean;
        public var xframe:String;
        public var sfxStop:Number;
        public var sfxStop2:Number;
        public var thrown:Boolean;

        public function NarutoKirby_274()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 13, this.frame14, 14, this.frame15, 21, this.frame22, 22, this.frame23, 29, this.frame30, 30, this.frame31, 33, this.frame34, 39, this.frame40, 41, this.frame42, 59, this.frame60, 60, this.frame61, 68, this.frame69, 83, this.frame84, 84, this.frame85, 86, this.frame87, 89, this.frame90, 96, this.frame97, 126, this.frame127);
        }

        public function afterHit(_arg_1:Event=null):void
        {
            this.gotoAndStop("afterHit");
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.afterHit);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.oodama = false;
                this.hasHit = false;
                this.xframe = null;
                this.thrown = false;
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.afterHit);
            };
        }

        internal function frame2():*
        {
            this.sfxStop = this.self.playAttackSound(3);
            this.sfxStop2 = this.self.playVoiceSound(3);
        }

        internal function frame3():*
        {
            this.self.playSound("naruto_bunshin");
            this.self.attachEffect("global_sparkle", {"y":-30});
        }

        internal function frame9():*
        {
            this.self.attachEffect("naruto_rasenChargeParticle");
        }

        internal function frame14():*
        {
            this.self.updateAttackStats({"cancelSoundOnEnd":true});
        }

        internal function frame15():*
        {
            this.xframe = "charging";
            this.self.attachEffect("naruto_rasenChargeParticle");
            this.self.attachEffect("global_dust_swirl");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame22():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame23():*
        {
            this.self.attachEffect("naruto_rasenChargeParticle");
        }

        internal function frame30():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame31():*
        {
            this.xframe = "attack";
            this.self.playVoiceSound(1);
            this.self.attachEffect("naruto_rasenChargeParticle");
            SSF2API.stopSound(this.sfxStop);
            SSF2API.stopSound(this.sfxStop2);
            this.self.updateAttackStats({
                "cancelSoundOnEnd":false,
                "cancelVoiceOnEnd":false
            });
        }

        internal function frame34():*
        {
            this.self.playSound("rasengan_sfx1");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame40():*
        {
            this.self.attachEffect("naruto_rasenUseParticle", {
                "x":this.flipX(-38),
                "y":27,
                "scaleX":1.4,
                "scaleY":1.4
            });
        }

        internal function frame42():*
        {
            this.thrown = false;
        }

        internal function frame60():*
        {
            this.self.endAttack();
        }

        internal function frame61():*
        {
            this.xframe = "attack";
            this.hasHit = true;
            if (this.oodama)
            {
                this.self.playSound("naruto_bunshin");
                this.self.stancePlayFrame("rasenshuriken");
            }
            else
            {
                this.self.fireProjectile("naruto_rasengan");
            };
            this.self.attachEffect("naruto_rasenUseParticle");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame69():*
        {
            this.self.attachEffect("naruto_rasenUseParticle");
        }

        internal function frame84():*
        {
            this.self.endAttack();
        }

        internal function frame85():*
        {
            this.xframe = "attack2";
            this.oodama = true;
            this.self.updateAttackBoxStats(1, {
                "hitStun":15,
                "priority":-1
            });
            this.self.updateAttackStats({
                "air_ease":2,
                "cancelSoundOnEnd":false,
                "cancelVoiceOnEnd":false,
                "allowControl":false
            });
            this.self.setXSpeed((this.self.getXSpeed() * 0.3));
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(35),
                "y":-35
            });
            if (this.hasHit)
            {
                this.self.playSound("rasengan_sfx1");
            };
            SSF2API.stopSound(this.sfxStop);
            SSF2API.stopSound(this.sfxStop2);
            this.self.playVoiceSound(2);
        }

        internal function frame87():*
        {
            this.self.attachEffect("naruto_rasenEffect2");
            this.self.attachEffect("global_dust_swirl");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame90():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame97():*
        {
            this.self.playSound("naruto_sfx_rasenshuriken");
            this.self.fireProjectile("rasenshuriken", 30, -15);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame127():*
        {
            this.self.endAttack();
        }


    }
}


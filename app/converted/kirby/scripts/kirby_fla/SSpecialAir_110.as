package kirby_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class SSpecialAir_110 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var landingBool:Boolean;

        public function SSpecialAir_110()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 13, this.frame14, 17, this.frame18, 25, this.frame26, 26, this.frame27, 33, this.frame34);
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.updateAttackStats({"allowControl":false});
            gotoAndStop("continue");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.landingBool = false;
            if (this.self && SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                this.self.playAttackSound(1);
            };
        }

        internal function frame7():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5,
                "parentLock":true
            });
        }

        internal function frame8():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
        }

        internal function frame14():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":15,
                "direction":35,
                "power":60
            });
            this.self.updateAttackBoxStats(2, {
                "damage":15,
                "direction":35,
                "power":60
            });
            this.self.refreshAttackID();
        }

        internal function frame18():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5,
                "parentLock":true
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }

        internal function frame27():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land2");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}


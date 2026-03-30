package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class UpSpecial_45 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var yVal:*;
        public var yInc:*;

        public function UpSpecial_45()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 7, this.frame8, 8, this.frame9, 9, this.frame10, 19, this.frame20, 25, this.frame26);
        }

        public function uSpecConstant():void
        {
            this.self.setYSpeed((this.yVal - this.yInc));
            this.yVal = this.self.getYSpeed();
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.yVal = this.self.getYSpeed();
                this.yInc = 3.5;
                this.self.attachEffect("global_sparkle", {"y":-30});
                if (!this.self.getMetalStatus())
                {
                    this.self.playAttackSound(1);
                };
            };
        }

        internal function frame4():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":-1.3,
                "y":-19.5,
                "parentLock":true
            });
        }

        internal function frame8():*
        {
            this.self.setYSpeed((this.yInc * 1.15));
        }

        internal function frame9():*
        {
            this.yVal = this.self.getYSpeed();
        }

        internal function frame10():*
        {
            this.self.createTimer(1, 9, this.uSpecConstant);
            this.self.updateAttackStats({"allowControl":true});
            this.self.attachEffect("global_dust_cloud");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("chibi_Prop_Quick", true);
            };
        }

        internal function frame20():*
        {
            if (this.self.isOnGround())
            {
                this.self.toLand();
            }
            else
            {
                this.self.destroyTimer(this.uSpecConstant);
                this.self.updateAttackStats({"refreshRate":-1});
                this.self.updateAttackBoxStats(1, {
                    "power":75,
                    "damage":4,
                    "selfHitStun":2,
                    "hitStun":3,
                    "kbConstant":120
                });
                this.self.refreshAttackID();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            };
        }

        internal function frame26():*
        {
            this.self.toHelpless();
        }


    }
}


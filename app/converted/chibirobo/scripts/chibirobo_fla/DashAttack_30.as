package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_30 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function DashAttack_30()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 13, this.frame14);
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
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame4():*
        {
            this.self.playAttackSound(1);
            this.self.setXSpeed(12, false);
            this.self.attachEffect("global_dust_light");
            this.self.addEffectToList(this.self.attachEffect("chibi_dashAttackTrail", {
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(45),
                "y":-15
            });
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}


package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_147 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var effect:*;

        public function DodgeRoll_147()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 15, this.frame16);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as KirbyExt);
            };
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame9():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}


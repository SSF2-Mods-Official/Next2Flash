package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Roll_67 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var effect:*;

        public function Roll_67()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 8, this.frame9, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
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


package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_25 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function HeavyLand_25()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            SSF2API.getCamera().shake(2);
            if (SSF2API.isReady())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("chibi_EStep");
                };
            };
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}


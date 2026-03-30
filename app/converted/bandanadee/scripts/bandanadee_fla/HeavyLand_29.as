package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_29 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function HeavyLand_29()
        {
            super();
            addFrameScript(0, this.frame1, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("effect_bdee_land", {"y":-13});
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("bandanadee_dashstop");
                };
            };
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}


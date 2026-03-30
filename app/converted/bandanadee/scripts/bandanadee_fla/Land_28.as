package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_28 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Land_28()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("effect_bdee_land", {"y":-20});
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("bandanadee_land1");
                };
            };
        }

        internal function frame4():*
        {
            this.self.endAttack();
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }


    }
}


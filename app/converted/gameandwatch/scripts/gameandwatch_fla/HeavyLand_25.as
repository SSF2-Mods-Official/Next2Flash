package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_25 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function HeavyLand_25()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(3);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("snd_se_GW_Landing02");
                };
            };
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}


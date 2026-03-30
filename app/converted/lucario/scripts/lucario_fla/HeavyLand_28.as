package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_28 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function HeavyLand_28()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                SSF2API.getCamera().shake(2);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("lucario_land02");
                };
            };
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}


package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_heavyland_25 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_heavyland_25()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(3);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("bomberman_landHeavy");
                };
            };
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}


package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_ledge_climb_83 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_ledge_climb_83()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 10, this.frame11, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame8():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame11():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}


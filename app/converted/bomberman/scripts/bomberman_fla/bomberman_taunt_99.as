package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_taunt_99 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_taunt_99()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 11, this.frame12, 22, this.frame23, 25, this.frame26, 28, this.frame29, 40, this.frame41, 48, this.frame49, 61, this.frame62);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame7():*
        {
            this.self.playSound("bomberman_slide");
        }

        internal function frame12():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame23():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }

        internal function frame29():*
        {
            this.self.playSound("bomberman_jumpflip");
        }

        internal function frame41():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame49():*
        {
            this.self.playSound("bomberman_slide");
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }


    }
}


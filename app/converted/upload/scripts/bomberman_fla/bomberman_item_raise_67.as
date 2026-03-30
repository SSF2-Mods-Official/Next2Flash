package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_raise_67 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_raise_67()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 20, this.frame21, 28, this.frame29, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame21():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame29():*
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

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}


package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_shoot_65 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_shoot_65()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}


package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHeavyShoot_66 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function ItemHeavyShoot_66()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}


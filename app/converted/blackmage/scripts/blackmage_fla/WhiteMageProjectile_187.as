package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class WhiteMageProjectile_187 extends MovieClip
    {

        public var self:*;
        public var character:*;
        public var lowestX:Number;
        public var highestX:Number;
        public var pos:Array;
        public var xCo:*;
        public var i:*;

        public function WhiteMageProjectile_187()
        {
            super();
            addFrameScript(0, this.frame1, 18, this.frame19, 64, this.frame65, 69, this.frame70);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
            };
        }

        internal function frame19():*
        {
            this.lowestX = 9999999;
            this.highestX = -9999999;
            if (this.character.getGlobalVariable("fsTargets").length > 0)
            {
                this.pos = this.character.getGlobalVariable("fsTargets");
                this.i = 0;
                while (this.i < this.pos.length)
                {
                    if (this.pos[this.i].getX() < this.lowestX)
                    {
                        this.lowestX = this.pos[this.i].getX();
                    };
                    if (this.pos[this.i].getX() > this.highestX)
                    {
                        this.highestX = this.pos[this.i].getX();
                    };
                    this.i++;
                };
            }
            else if (this.self.isFacingRight())
            {
                this.lowestX = (this.self.getX() + 200);
                this.highestX = (this.self.getX() + 200);
            }
            else
            {
                this.lowestX = (this.self.getX() - 200);
                this.highestX = (this.self.getX() - 200);
            };
            this.xCo = (this.lowestX + ((this.highestX - this.lowestX) / 2));
            this.character.fireProjectile("bm_fs_holy", this.xCo, this.self.getY(), true);
        }

        internal function frame65():*
        {
            this.self.attachEffect("bm_fs_warp");
            this.self.playSound("bm_Warp_part2");
        }

        internal function frame70():*
        {
            this.self.destroy();
        }


    }
}


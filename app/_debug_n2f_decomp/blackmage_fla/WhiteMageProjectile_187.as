package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class WhiteMageProjectile_187 extends MovieClip {
        public var self:*;
        public var character:*;
        public var lowestX:Number;
        public var highestX:Number;
        public var pos:Array;
        public var xCo:*;
        public var i:*;
        public function WhiteMageProjectile_187() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(18, frame_19);
            addFrameScript(64, frame_65);
            addFrameScript(69, frame_70);
        }
        internal function frame_1():* {
            var self:*;
            var character:*;
            var lowestX:Number;
            var highestX:Number;
            var pos:Array;
            var xCo:*;
            var i:*;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                        };
        }
        internal function frame_19():* {
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
        internal function frame_65():* {
            this.self.attachEffect("bm_fs_warp");
                        this.self.playSound("bm_Warp_part2");
        }
        internal function frame_70():* {
            this.self.destroy();
        }
    }
}
